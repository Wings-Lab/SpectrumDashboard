# Developers : Isha Khanna and Daljeet Singh Chhabra

from pymongo import *
from bson.json_util import dumps
from helpers import mac_encode, UserEquipment, UE_Measurement

HOSTNAME = 'localhost'
PORT = 27017
DBNAME = 'test'


def getReadingsinRadius(lat=0, lon=0, radius=0):
    client = MongoClient(HOSTNAME, PORT)

    db = client[DBNAME]

    ue_measurements = db['UE_Measurements']
    ue_registered = db['Registered_UE']

    # print ue_measurements.find().count

    #  Works Correctly for the Polygon.
    # ue_measurements.find(
    #     {'loc': {
    #        '$geoWithin': {
    #           '$geometry': {
    #              'type' : "Polygon" ,
    #              'coordinates': [ [ [ 0, 0 ], [ 3, 6 ], [ 6, 1 ], [ 0, 0 ] ] ]
    #           }
    #        }
    #      }
    #    }
    # ).count()


    #  Within Sphere :

    # Earth Radian factor = 3959
    # Might need to run db.getCollection('UE_Measurements').ensureIndex({point:"2dsphere"}); on db
    r = (float)(radius)/5
    dataOutput = ue_measurements.find({'loc': {'$geoWithin':
                                                   {'$centerSphere': [[lon, lat], r]
                                                    }}})
    # dataOutput = ue_measurements.find({'loc': {'$geoWithin':
    #                                                {'$center': [[lon, lat], radius / 3959]
    #                                                 }}})

    channel_pow = {}
    macs = []

    for doc in dataOutput:
        if doc["mac"] not in macs:
            macs.append(doc["mac"])
        channel = doc["ue_channel_scanned"]
        if (channel_pow.has_key(channel)):
            sum = channel_pow[channel][0]
            count = channel_pow[channel][1]
            channel_pow[channel] = [sum + doc["ue_channel_scanned_power"], count + 1]
        else:
            channel_pow[channel] = [doc["ue_channel_scanned_power"], 1]

    table1Data = []
    table2Data = []

    ue_registered_output = ue_registered.find({'_id': {'$in': macs}})

    for doc in ue_registered_output:
        table2Data.append({"mac": doc["_id"], "ue_status": doc["ue_status"]})

    for key in channel_pow.keys():
        val = channel_pow[key]
        pow = val[0] / val[1]
        channel_pow[key] = pow
        table1Data.append({"channel": key, "power": pow})

    finalData = {'table1': table1Data, 'table2': table2Data}

    # return dumps(dataOutput)
    return dumps(finalData)


def getChannels():
    client = MongoClient(HOSTNAME, PORT)

    db = client[DBNAME]

    ue_measurements = db['UE_Measurements']

    dataOutput = ue_measurements.distinct('ue_channel_scanned')
    results = [int(i) for i in dataOutput]
    results.sort()
    return results

def getUEMeasurements(channel):
    client = MongoClient(HOSTNAME, PORT)

    db = client[DBNAME]

    ue_measurements = db['UE_Measurements']

    dataOutput = ue_measurements.find({'ue_channel_scanned': channel})
    return dumps(dataOutput)


def populate_ue_from_db_entry(ue, entry, ue_measurements):
    ue.id = mac_encode(entry["_id"])
    ue.mac = entry["_id"]
    ue.model = entry["ue_model"]
    ue.status = entry["ue_status"]
    ue.total_measurements = ue_measurements.find().count()
    ue_meas = ue_measurements.find({'mac': ue.mac}).sort("last_scanned", DESCENDING).limit(1)
    if ue_meas.count() > 0:
        measurement = ue_meas[0]
        ue.last_latitude = measurement["loc"]["coordinates"][1]
        ue.last_longitude = measurement["loc"]["coordinates"][0]
        ue.last_scantime = measurement["last_scanned"]
    else:
        ue.last_latitude = "N/A"
        ue.last_longitude = "N/A"
        ue.last_scantime = "N/A"


def getAllRegisteredUEData():
    client = MongoClient(HOSTNAME, PORT)
    db = client[DBNAME]
    ue_measurements = db['UE_Measurements']
    ue_registered = db['Registered_UE']
    all_ue_registered = ue_registered.find().sort('ue_status', DESCENDING)

    finalData = []

    for entry in all_ue_registered:
        ue = UserEquipment()
        populate_ue_from_db_entry(ue, entry, ue_measurements)
        finalData.append(ue)
    return finalData


def findUEFromMac(mac):
    client = MongoClient(HOSTNAME, PORT)
    db = client[DBNAME]
    ue_measurements = db['UE_Measurements']
    ue_registered = db['Registered_UE']
    result = ue_registered.find({"_id": mac}).limit(1)
    if result.count() > 0:
        entry = result[0]
    else:
        return None
    ue = UserEquipment()
    populate_ue_from_db_entry(ue, entry, ue_measurements)
    # all_measurements = ue_measurements.find({"mac" : ue.mac}).sort("last_scanned", ASCENDING)
    all_measurements = ue_measurements.find({"mac" : ue.mac}).sort("last_scanned", DESCENDING).limit(20).sort("last_scanned", ASCENDING)
    for measurement_entry in all_measurements:
        measurement = UE_Measurement()
        measurement.battery_level = measurement_entry["ue_battery_power"]
        measurement.channel_power = measurement_entry["ue_channel_scanned_power"]
        measurement.channel = measurement_entry["ue_channel_scanned"]
        measurement.latitude = measurement_entry["loc"]["coordinates"][1]
        measurement.longitude = measurement_entry["loc"]["coordinates"][0]
        measurement.scan_time = measurement_entry["last_scanned"]
        ue.measurements.append(measurement)
    return ue

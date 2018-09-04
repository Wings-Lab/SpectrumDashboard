def mac_encode(mac_addr):
    return ''.join(mac_addr.split(':'))


def chunkstring(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def mac_decode(mac_addr):
    return ':'.join(list(chunkstring(mac_addr, 2)))


class UserEquipment:
    def __init__(self):
        self.id = ""
        self.mac = ""
        self.model = ""
        self.status = ""
        # Cached fields
        self.last_latitude = ""
        self.last_longitude = ""
        self.last_scantime = ""
        # Measurements list
        self.total_measurements = 0
        self.measurements = []


class UE_Measurement:
    def __init__(self):
        # self.id, self.mac
        self.scan_time = ""
        self.latitude = ""
        self.longitude = ""
        self.channel = ""
        self.channel_power = ""
        self.battery_level = ""

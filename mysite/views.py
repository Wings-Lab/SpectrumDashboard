# Developers : Daljeet Singh Chhabra and Isha Khanna

from django.shortcuts import render
from django.http import HttpResponse, Http404
import db_adapter
from helpers import mac_decode

def heatmap(request):
    if request.is_ajax():
        if request.method == 'POST':
            channel = request.POST.get('txn')
            json_data = db_adapter.getUEMeasurements(channel)
            return HttpResponse(json_data, content_type='application/json')
        else:
            return HttpResponse(status=201)
    else:
        json_data = db_adapter.getChannels()
        return render(request, "heatmap.html", {"channels": json_data})

def geo_query(request):
    if request.is_ajax():
        lat = float(request.POST.get('lat'))
        lon = float(request.POST.get('lon'))
        rad = float(request.POST.get('rad'))
        json_data = db_adapter.getReadingsinRadius(lat, lon, rad)
        return HttpResponse(json_data, content_type='application/json')
    else:
        #Dunno what to do
        return HttpResponse(status=201)

def ue_info(request):
    data = db_adapter.getAllRegisteredUEData()
    return render(request, "uelist.html", {"ue_list":data})

def ue_detail(request, ue_id):
    mac = mac_decode(ue_id)
    ue = db_adapter.findUEFromMac(mac)
    if ue is None:
        raise Http404("UE Not found")
    return render(request, "ue_details.html", {"ue" : ue})

def static_view(request):
    """
    serve pages directly from the templates directories.
    """
    return render(request, "homepage.html")

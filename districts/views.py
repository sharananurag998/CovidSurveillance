from django.shortcuts import render
from districts.models import DistrictsModel
import requests
import datetime
# Create your views here.

def hello_world(request):
    return render(request, 'homepage.html', {})

def apinotfound(request):
    return render(request, 'api_not_found.html', {})

def district_index_refresh(request):
    response = requests.get('https://api.covid19india.org/zones.json')
    zonedata = response.json()
    p = DistrictsModel.objects.all()
    p.delete()
    for i in zonedata.items():
        for j in i[1]:
            p = DistrictsModel(state=j['state'], district=j['district'], zone=j['zone'], lastupdated=datetime.datetime.now())
            p.save()
    districts = DistrictsModel.objects.all()
    context = {
        'districts': districts
    }
    
    return render(request, 'district_index.html', context)

def district_index_display(request):
    districts = DistrictsModel.objects.all()
    context = {
        'districts': districts
    }
    
    return render(request, 'district_index.html', context)

def district_detail(request, pk):
    district = DistrictsModel.objects.get(pk=pk)
    context = {
        'district' : district
    }
    return render(request, 'district_detail.html', context)

def state_detail(request, state):
    state_dists = DistrictsModel.objects.filter(state=state)
    context = {
        'districts': state_dists,
        'state' : state,
    }
    return render(request, 'state_detail.html', context)


def district_detail_with_state(request, pk, state):
    district = DistrictsModel.objects.get(pk=pk)
    context = {
        'district' : district,
        'state' : state,
    }
    return render(request, 'district_detail.html', context)

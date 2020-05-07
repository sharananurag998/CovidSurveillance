from django.shortcuts import render
from home.models import HomeModel
import requests
import datetime
# Create your views here.

def hello_world(request):
    return render(request, 'homepage.html', {})

def district_index_refresh(request):
    response = requests.get('https://api.covid19india.org/zones.json')
    zonedata = response.json()
    p = HomeModel.objects.all()
    p.delete()
    for i in zonedata.items():
        for j in i[1]:
            p = HomeModel(state=j['state'], district=j['district'], zone=j['zone'], lastupdated=datetime.datetime.now())
            p.save()
    districts = HomeModel.objects.all()
    context = {
        'districts': districts
    }
    
    return render(request, 'district_index.html', context)

def district_index_display(request):
    districts = HomeModel.objects.all()
    context = {
        'districts': districts
    }
    
    return render(request, 'district_index.html', context)

def district_detail(request, pk):
    district = HomeModel.objects.get(pk=pk)
    context = {
        'district' : district
    }
    return render(request, 'district_detail.html', context)
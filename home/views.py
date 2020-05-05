from django.shortcuts import render
from home.models import HomeModel
# Create your views here.

def hello_world(request):
    return render(request, 'homepage.html', {})

def district_index(request):
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
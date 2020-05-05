from django.urls import path
from home import views

urlpatterns = [
    path('', views.district_index, name='district_index'),
    path("<int:pk>/", views.district_detail, name='district_detail'),
]


from django.urls import path
from social_distance_monitor import views

urlpatterns = [
    path('', views.social_distancing_index, name="social_distancing_index"),
    path('data', views.social_distance_monitor, name="social_distancing_index_data"),
]

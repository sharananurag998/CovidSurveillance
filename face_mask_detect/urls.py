from django.urls import path
from face_mask_detect import views

urlpatterns = [
    path('', views.surveillance_view, name="surveillance_index"),
    path('data', views.get_surveillance_data, name="surveillance_index_data"),
]

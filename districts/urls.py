from django.urls import path
from districts import views

urlpatterns = [
    path('', views.district_index_display, name='district_index_display'),
    path('refresh/', views.district_index_refresh, name='district_index_refresh'),
    path("<int:pk>/", views.district_detail, name='district_detail'),
]


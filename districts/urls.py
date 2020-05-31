from django.urls import path
from districts import views

urlpatterns = [
    path('', views.district_index_display, name='district_index_display'),
    path('refresh/', views.district_index_refresh, name='district_index_refresh'),
    path("<int:pk>/", views.district_detail, name='district_detail'),
    path('apinotfound/', views.apinotfound, name='api_not_found'),
    path("state/<str:state>/", views.state_detail, name='state_detail'),
    path("<int:pk>/<str:state>/", views.district_detail_with_state, name='district_detail_with_state'),
]


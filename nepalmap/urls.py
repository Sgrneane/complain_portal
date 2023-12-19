from django.urls import path
from . import views

app_name='nepalmap'


urlpatterns = [
    path('get-districts/<int:id>/',views.get_district,name='get_district'),
    path('get-district/get-municipalities/<int:id>/',views.get_municipality,name="get_municipality")
]
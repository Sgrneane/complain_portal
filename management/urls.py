from django.urls import path
from . import views

app_name='management'


urlpatterns = [
    path('', views.index, name='index'),
    path('user-dashboard',views.user_dashboard,name='user_dashboard'),
    path('anonymous-complain',views.anonymous_complain,name='anonymous_complain'),
    path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('all-complains',views.all_complains,name='all_complains'),
    path('create-complain',views.create_complain,name='create_complain'),
    path('my-complains',views.my_complains,name='my_complains'),
    path('complain-view/<int:id>',views.view_complain,name='view_complain'),
    path('category-list',views.category_list,name='category_list'),
    path('create-category',views.create_category,name='create_category'),
    path('create-sub-category',views.create_sub_category, name='create_sub_category'),
    path('create-communication/<int:id>',views.create_communication,name='create_communication'),
    path('response/<int:id>',views.response, name="response")
]
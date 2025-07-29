from django.urls import path
from . import views

urlpatterns = [
    path('', views.home ,name='home'),
    # path('home/', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('list/', views.list, name='list'),
    path('listdata/<int:id>/', views.show, name='view_list'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('send_kena/', views.send_kena, name='send_kena'),
    path('send_kena/<int:id>/', views.send_kena, name='send_kena_with_id'),

    path('register/', views.register, name='register'),    
    path('logout/', views.logout_view, name='logout'),
]

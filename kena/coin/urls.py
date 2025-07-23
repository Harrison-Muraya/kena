from django.urls import path
from . import views

urlpatterns = [
    path('', views.home ,name='home'),
    # path('home/', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('list/', views.list, name='list'),
    path('listdata/<int:id>/', views.show, name='view_list'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
]

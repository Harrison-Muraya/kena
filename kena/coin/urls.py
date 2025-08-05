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
    path('mine_kena/', views.mine_kena, name='mine_kena'),
    
    path('register/', views.register, name='register'),    
    path('logout/', views.logout_view, name='logout'),

    # API links
    path('api/get_mine_data', views.get_mine_data, name='get_mine_data'),
    path('api/submit_hash', views.submit_block, name='submt_hash'),
    path('api/download-miner/', views.download_miner_script, name='download_miner'),

]

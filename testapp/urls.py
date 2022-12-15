from django.urls import path

from . import views, auth

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),
    path('embed-info/', views.get_embed_info, name='embed-info'),
    path('report/', views.ReportView.as_view(), name='report'),
]
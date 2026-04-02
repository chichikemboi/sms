from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.root_view, name='root'),
    path('home/', views.home_view, name='home'),
]

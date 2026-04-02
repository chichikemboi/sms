from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='list'),
    path('new/', views.item_create, name='create'),
    path('<int:pk>/edit/', views.item_edit, name='edit'),
    path('<int:pk>/delete/', views.item_delete, name='delete'),
]

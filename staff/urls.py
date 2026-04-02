from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list, name='list'),
    path('<int:pk>/', views.staff_detail, name='detail'),
    path('<int:pk>/edit/', views.staff_edit, name='edit'),
]

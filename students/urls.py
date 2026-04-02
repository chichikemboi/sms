from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('new/', views.student_create, name='create'),
    path('<int:pk>/', views.student_detail, name='detail'),
    path('<int:pk>/edit/', views.student_edit, name='edit'),
    # Guardians
    path('guardians/', views.guardian_list, name='guardian_list'),
    path('guardians/new/', views.guardian_create, name='guardian_create'),
    path('guardians/<int:pk>/edit/', views.guardian_edit, name='guardian_edit'),
]

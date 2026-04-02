from django.urls import path
from . import views

app_name = 'lessons'

urlpatterns = [
    path('', views.lesson_list, name='list'),
    path('new/', views.lesson_create, name='create'),
    path('<int:pk>/', views.lesson_detail, name='detail'),
    path('<int:pk>/edit/', views.lesson_edit, name='edit'),
    path('coverage/', views.coverage_home, name='coverage_home'),
    path('coverage/<int:section_pk>/<int:subject_pk>/', views.syllabus_coverage, name='coverage'),
]

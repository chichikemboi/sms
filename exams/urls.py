from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list, name='list'),
    path('new/', views.exam_create, name='create'),
    path('<int:exam_pk>/enter/', views.mark_entry_select, name='mark_entry_select'),
    path('<int:exam_pk>/enter/<int:section_pk>/<int:subject_pk>/', views.mark_entry, name='mark_entry'),
    path('<int:exam_pk>/results/<int:section_pk>/', views.results_analysis, name='results'),
]

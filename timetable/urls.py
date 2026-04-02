from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.timetable_home, name='home'),
    path('<int:section_pk>/', views.timetable_view, name='view'),
    path('<int:section_pk>/edit/<int:day>/<int:period_pk>/', views.slot_edit, name='slot_edit'),
]

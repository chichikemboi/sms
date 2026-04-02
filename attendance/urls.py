from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_home, name='home'),
    path('<int:section_pk>/mark/', views.mark_attendance, name='mark'),
    path('<int:section_pk>/report/', views.attendance_report, name='report'),
]

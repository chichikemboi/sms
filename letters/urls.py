from django.urls import path
from . import views

app_name = 'letters'

urlpatterns = [
    path('', views.letters_home, name='home'),
    path('report-card/<int:student_pk>/<int:exam_pk>/', views.report_card_pdf, name='report_card'),
    path('fee-statement/<int:student_pk>/', views.fee_statement_pdf, name='fee_statement'),
    path('class-reports/<int:exam_pk>/<int:section_pk>/', views.class_report_cards, name='class_reports'),
]

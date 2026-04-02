from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_dashboard, name='dashboard'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/new/', views.payment_create, name='payment_create'),
    path('student/<int:student_pk>/', views.student_fee_detail, name='student_detail'),
]

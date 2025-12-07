from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-class/', views.add_class, name='add_class'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('class/<int:class_id>/add-student/', views.add_student, name='add_student'),
    path('class/<int:class_id>/delete/', views.delete_class, name='delete_class'),
    path('attendance/<int:attendance_id>/edit/', views.edit_attendance, name='edit_attendance'),
    path('public/<int:class_id>/', views.public_view, name='public_view'),
]

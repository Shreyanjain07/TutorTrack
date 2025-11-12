from django.contrib import admin
from .models import ClassRoom, Student, Attendance

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_at')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'classroom', 'parent_email')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'start_time', 'end_time')
    list_filter = ('status', 'date')
from django.db import models
from django.utils import timezone
from datetime import datetime, date
import uuid

class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Student(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='students')
    name = models.CharField(max_length=100)
    parent_email = models.EmailField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    public_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=(('Present', 'Present'), ('Absent', 'Absent'), ('Cancelled', 'Cancelled')),
        default='Present'
    )
    remarks = models.TextField(blank=True, null=True)

    @property
    def total_hours(self):
        """Automatically calculate total hours for each record"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return round(delta.total_seconds() / 3600, 2)
        return 0

    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.status})"

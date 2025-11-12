from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import ClassRoom, Student, Attendance
from django.contrib import messages
from datetime import timedelta, date

def dashboard(request):
    classes = ClassRoom.objects.all()
    total_students = Student.objects.count()
    total_attendance = Attendance.objects.count()
    return render(request, 'dashboard.html', {
        'classes': classes,
        'total_students': total_students,
        'total_attendance': total_attendance
    })


def class_detail(request, class_id):
    classroom = get_object_or_404(ClassRoom, id=class_id)
    students = classroom.students.all()
    attendance_records = Attendance.objects.filter(student__in=students).order_by('-start_time')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')

        if student_id and start_time and end_time:
            student = get_object_or_404(Student, id=student_id)
            Attendance.objects.create(
                student=student,
                start_time=start_time,
                end_time=end_time,
                status=status,
                remarks=remarks,
            )
            return redirect('class_detail', class_id=class_id)

    context = {
        'classroom': classroom,
        'students': students,
        'attendance_records': attendance_records,
    }
    return render(request, 'class_detail.html', context)

    
def add_class(request):
    if request.method == "POST":
        name = request.POST.get("name")
        subject = request.POST.get("subject")

        if name and subject:
            ClassRoom.objects.create(name=name, subject=subject)
            return redirect('dashboard')

    return render(request, 'add_class.html')    

def add_student(request, class_id):
    classroom = get_object_or_404(ClassRoom, id=class_id)

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        if name:
            Student.objects.create(
                name=name,
                phone=phone,
                email=email,
                classroom=classroom  # make sure this matches your FK field name
            )
            return redirect('class_detail', class_id=classroom.id)

    return render(request, 'add_student.html', {'classroom': classroom})

def delete_class(request, class_id):
    classroom = get_object_or_404(ClassRoom, id=class_id)

    if request.method == "POST":
        classroom.delete()
        messages.success(request, f'Class "{classroom.name}" has been deleted successfully.')
        return redirect('dashboard')

    return render(request, 'delete_class.html', {'classroom': classroom})


    #  Weekly/monthly summaries
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = date(today.year, today.month, 1)

    attendance_this_week = Attendance.objects.filter(
        student__classroom=classroom,
        date__range=[week_start, week_end],
        status='Present'
    )

    attendance_records = Attendance.objects.filter(student__classroom=classroom).order_by('-date')

    return render(request, 'class_detail.html', {
        'classroom': classroom,
        'students': students,
        'attendance_records': attendance_records,
    })


def public_view(request, class_id):
    classroom = get_object_or_404(ClassRoom, id=class_id)
    students = classroom.students.all()
    attendance_records = Attendance.objects.filter(student__in=students).order_by('-start_time')

    # Compute total attendance hours and stats
    total_present = attendance_records.filter(status="Present").count()
    total_absent = attendance_records.filter(status="Absent").count()
    total_hours = 0

    for record in attendance_records:
        if record.end_time and record.start_time:
            duration = record.end_time - record.start_time
            total_hours += duration.total_seconds() / 3600

    context = {
        'classroom': classroom,
        'attendance_records': attendance_records,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_hours': round(total_hours, 1),
    }
    return render(request, 'public_view.html', context)
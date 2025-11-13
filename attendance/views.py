from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import ClassRoom, Student, Attendance
from django.contrib import messages
from datetime import timedelta, datetime, time

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
        date = request.POST.get("date")
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')

        if student_id and start_time and end_time:
            student = get_object_or_404(Student, id=student_id)
            Attendance.objects.create(
                student=student,
                date = date,
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
    attendance_records = Attendance.objects.filter(student__classroom=classroom)

    total_present = attendance_records.filter(status='Present').count()
    total_absent = attendance_records.filter(status='Absent').count()

    # Calculate total hours safely
    total_hours = 0
    for a in attendance_records:
        try:
            if isinstance(a.start_time, time) and isinstance(a.end_time, time):
                # Handle older records that only have time (not datetime)
                start_dt = datetime.combine(a.date, a.start_time)
                end_dt = datetime.combine(a.date, a.end_time)
            else:
                # Normal case: start_time and end_time are datetimes
                start_dt, end_dt = a.start_time, a.end_time

            delta = (end_dt - start_dt).total_seconds() / 3600
            total_hours += delta if delta > 0 else 0
        except Exception:
            continue  # Skip records with missing or invalid data

    total_hours = round(total_hours, 2)

    return render(request, 'public_view.html', {
        'classroom': classroom,
        'attendance_records': attendance_records,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_hours': total_hours
    })
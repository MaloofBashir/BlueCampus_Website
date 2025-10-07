from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Certificate, StudentSemester
from django.utils import timezone
import base64

def index(request):
    return render(request,"studentcorner/home.html")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
from .models import Student, Certificate, StudentSemester
from .pdf_generator import generate_bonafide_certificate

def bonafide_certificate(request):
    student = None
    student_semesters = None
    certificate_history = None
    can_issue = True
    last_certificate_date = None
    latest_semester = None
    
    if request.method == 'POST':
        if 'search' in request.POST:
            search_term = request.POST.get('search_term')
            try:
                student = Student.objects.get(
                    Q(u_registration_no=search_term) | Q(class_roll_no=search_term)
                )
                student_semesters = StudentSemester.objects.filter(student=student).order_by('-session__start_date')
                latest_semester = student_semesters.first() if student_semesters.exists() else None
                
                certificate_history = Certificate.objects.filter(
                    student=student, 
                    certificate_type='bonafide'
                ).order_by('-issue_date')
                
                if certificate_history.exists():
                    last_certificate = certificate_history.first()
                    last_certificate_date = last_certificate.issue_date
                    days_since = (timezone.now().date() - last_certificate_date).days
                    if days_since < 180:
                        can_issue = False
                        remaining_days = 180 - days_since
                        messages.warning(request, f'Cannot issue certificate. Last certificate was issued on {last_certificate_date}. Please wait {remaining_days} more days.')
                
            except Student.DoesNotExist:
                messages.error(request, 'Student not found with this registration/roll number')
        
        elif 'issue_certificate' in request.POST:
            student_id = request.POST.get('student_id')
            student = get_object_or_404(Student, id=student_id)
            
            # IMPORTANT: Check if certificate can be issued AGAIN before creating
            certificate_history = Certificate.objects.filter(
                student=student, 
                certificate_type='bonafide'
            ).order_by('-issue_date')
            
            can_issue = True
            if certificate_history.exists():
                last_certificate = certificate_history.first()
                last_certificate_date = last_certificate.issue_date
                days_since = (timezone.now().date() - last_certificate_date).days
                if days_since < 180:
                    can_issue = False
                    remaining_days = 180 - days_since
                    messages.error(request, f'Cannot issue certificate! Last certificate was issued on {last_certificate_date}. Please wait {remaining_days} more days.')
                    
                    # Reload student data to show the restriction
                    student_semesters = StudentSemester.objects.filter(student=student).order_by('-session__start_date')
                    latest_semester = student_semesters.first() if student_semesters.exists() else None
                    
                    context = {
                        'student': student,
                        'student_semesters': student_semesters,
                        'certificate_history': certificate_history,
                        'can_issue': False,
                        'last_certificate_date': last_certificate_date,
                        'latest_semester': latest_semester,
                    }
                    return render(request, 'studentcorner/bonafide.html', context)
            
            # Only create certificate if allowed
            if can_issue:
                latest_semester = StudentSemester.objects.filter(student=student).order_by('-session__start_date').first()

                certificate = Certificate.objects.create(
                    student=student,
                    student_semester=latest_semester,
                    certificate_type='bonafide',
                    issue_date=timezone.now().date(),
                    purpose=request.POST.get('purpose', ''),
                    remarks=request.POST.get('remarks', ''),
                    issued_by=request.user.username if request.user.is_authenticated else 'Admin'
                )

                # Generate PDF buffer
                pdf_buffer = generate_bonafide_certificate(student, certificate, latest_semester)

                # Convert BytesIO to Base64
                pdf_bytes = pdf_buffer.getvalue()
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

                # Reload certificate history AFTER creating new certificate
                certificate_history = Certificate.objects.filter(
                    student=student, 
                    certificate_type='bonafide'
                ).order_by('-issue_date')
                
                # Update can_issue flag - NOW it should be False since we just issued one
                can_issue = False
                last_certificate_date = certificate.issue_date
                
                # Reload student semesters
                student_semesters = StudentSemester.objects.filter(student=student).order_by('-session__start_date')

                messages.success(request, f'Bonafide certificate issued successfully on {certificate.issue_date}!')

                context = {
                    'student': student,
                    'student_semesters': student_semesters,
                    'certificate_history': certificate_history,
                    'can_issue': False,  # IMPORTANT: Set to False after issuing
                    'last_certificate_date': last_certificate_date,  # Show the date just issued
                    'latest_semester': latest_semester,
                    'preview_pdf_base64': pdf_base64,
                    'clear_form': True,  # Flag to clear form fields
                }

                return render(request, 'studentcorner/bonafide.html', context)
    
    context = {
        'student': student,
        'student_semesters': student_semesters,
        'certificate_history': certificate_history,
        'can_issue': can_issue,
        'last_certificate_date': last_certificate_date,
        'latest_semester': latest_semester,
    }
    return render(request, 'studentcorner/bonafide.html', context)



def download_bonafide_pdf(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id, certificate_type='bonafide')
    student = certificate.student
    student_semester = certificate.student_semester
    
    # Generate PDF
    pdf_buffer = generate_bonafide_certificate(student, certificate, student_semester)
    
    # Serve PDF inline
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    filename = f"bonafide_{student.u_registration_no}_{certificate.issue_date}.pdf"
    # Inline display for iframe
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response




# Add to your views.py
from django.db.models import Count, Q
from django.http import JsonResponse
from collections import defaultdict
def student_statistics(request):
    """Main statistics dashboard with detailed subject-wise breakdown"""
    # Get all active students
    active_students = Student.objects.filter(is_active=True)
    
    # Overall statistics
    total_students = active_students.count()
    male_students = active_students.filter(gender='M').count()
    female_students = active_students.filter(gender='F').count()
    
    # Batch-wise statistics - FIXED: removed student__ prefix since we're already on Student model
    batch_stats = active_students.values('batch').annotate(
        total=Count('id'),
        male=Count('id', filter=Q(gender='M')),
        female=Count('id', filter=Q(gender='F'))
    ).order_by('batch')
    
    # Semester-wise enrollment
    semester_enrollment = StudentSemester.objects.filter(
        is_enrolled=True,
        student__is_active=True
    ).values(
        'semester__semester_number', 
        'semester__semester_name'
    ).annotate(
        total=Count('id'),
        male=Count('id', filter=Q(student__gender='M')),
        female=Count('id', filter=Q(student__gender='F'))
    ).order_by('semester__semester_number')
    
    # Detailed subject-wise statistics for each course type
    course_type_details = {}
    
    # Define all course types and their display names
    course_types = {
        'major_course': 'Major Courses',
        'minor_course': 'Minor Courses', 
        'md1': 'Multidisciplinary 1',
        'md2': 'Multidisciplinary 2',
        'skill': 'Skill Enhancement',
        'vac1': 'Value Added Course 1',
        'vac2': 'Value Added Course 2',
        'aec': 'Ability Enhancement Course',
    }
    
    # Get detailed subject counts for each course type
    for course_field, display_name in course_types.items():
        subject_stats = StudentSemester.objects.filter(
            is_enrolled=True,
            student__is_active=True,
            **{f'{course_field}__isnull': False}
        ).values(
            f'{course_field}__subject_code',
            f'{course_field}__subject_name',
            f'{course_field}__course_type'
        ).annotate(
            total_students=Count('id'),
            male_students=Count('id', filter=Q(student__gender='M')),
            female_students=Count('id', filter=Q(student__gender='F'))
        ).order_by(f'{course_field}__subject_name')
        
        course_type_details[course_field] = {
            'display_name': display_name,
            'subjects': list(subject_stats),
            'total_enrollments': sum([subject['total_students'] for subject in subject_stats])
        }
    
    # Overall course type summary (without subject details)
    course_type_summary = []
    for course_field, display_name in course_types.items():
        stats = StudentSemester.objects.filter(
            is_enrolled=True,
            student__is_active=True,
            **{f'{course_field}__isnull': False}
        ).aggregate(
            total=Count('id'),
            male=Count('id', filter=Q(student__gender='M')),
            female=Count('id', filter=Q(student__gender='F'))
        )
        
        course_type_summary.append({
            'type': course_field,
            'name': display_name,
            'total': stats['total'],
            'male': stats['male'],
            'female': stats['female']
        })
    
    context = {
        'total_students': total_students,
        'male_students': male_students,
        'female_students': female_students,
        'batch_stats': batch_stats,
        'semester_enrollment': semester_enrollment,
        'course_type_details': course_type_details,
        'course_type_summary': course_type_summary,
    }
    
    return render(request, 'studentcorner/statistics.html', context)

def detailed_semester_stats(request, semester_number):
    """Detailed statistics for a specific semester"""
    semester_stats = StudentSemester.objects.filter(
        semester__semester_number=semester_number,
        is_enrolled=True,
        student__is_active=True
    )
    
    # Major subjects in this semester
    major_subjects = semester_stats.filter(
        major_course__isnull=False
    ).values(
        'major_course__subject_code',
        'major_course__subject_name'
    ).annotate(
        total=Count('id'),
        male=Count('id', filter=Q(student__gender='M')),
        female=Count('id', filter=Q(student__gender='F'))
    ).order_by('major_course__subject_name')
    
    # Minor subjects in this semester
    minor_subjects = semester_stats.filter(
        minor_course__isnull=False
    ).values(
        'minor_course__subject_code',
        'minor_course__subject_name'
    ).annotate(
        total=Count('id'),
        male=Count('id', filter=Q(student__gender='M')),
        female=Count('id', filter=Q(student__gender='F'))
    ).order_by('minor_course__subject_name')
    
    # Overall semester stats
    overall_stats = semester_stats.aggregate(
        total=Count('id'),
        male=Count('id', filter=Q(student__gender='M')),
        female=Count('id', filter=Q(student__gender='F'))
    )
    
    context = {
        'semester_number': semester_number,
        'overall_stats': overall_stats,
        'major_subjects': major_subjects,
        'minor_subjects': minor_subjects,
        'total_students': semester_stats.count(),
    }
    
    return render(request, 'studentcorner/semester_detail.html', context)


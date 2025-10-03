from django.contrib import admin


from .models import (
    AcademicSession, Semester, Subject,
    Student, StudentSemester, Certificate
)

@admin.register(StudentSemester)
class StudentSemesterAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'semester', 'is_enrolled']
    list_filter = ['session', 'semester', 'is_enrolled']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "major_course":
            kwargs["queryset"] = Subject.objects.filter(course_type='MAJOR')
        elif db_field.name == "minor_course":
            kwargs["queryset"] = Subject.objects.filter(course_type='MINOR')
        elif db_field.name == "md1":
            kwargs["queryset"] = Subject.objects.filter(course_type='MD1')
        elif db_field.name == "md2":
            kwargs["queryset"] = Subject.objects.filter(course_type='MD2')
        elif db_field.name == "skill":
            kwargs["queryset"] = Subject.objects.filter(course_type='SKILL')
        elif db_field.name == "vac1":
            kwargs["queryset"] = Subject.objects.filter(course_type='VAC1')
        elif db_field.name == "vac2":
            kwargs["queryset"] = Subject.objects.filter(course_type='VAC2')
        elif db_field.name == "aec":
            kwargs["queryset"] = Subject.objects.filter(course_type='AEC')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('session_code', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('session_code',)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('semester_number', 'semester_name')
    ordering = ('semester_number',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name', 'course_type')
    list_filter = ('course_type',)
    search_fields = ('subject_code', 'subject_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'u_registration_no', 'class_roll_no', 'batch', 'course_name', 'is_active')
    list_filter = ('batch', 'course_name', 'is_active', 'gender')
    search_fields = ('student_name', 'u_registration_no', 'class_roll_no')

# @admin.register(StudentSemester)
# class StudentSemesterAdmin(admin.ModelAdmin):
#     list_display = ('student', 'session', 'semester', 'is_enrolled')
#     list_filter = ('session', 'semester', 'is_enrolled')
#     search_fields = ('student__student_name', 'student__u_registration_no')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'get_student_name', 'get_registration_no', 'certificate_type', 'issue_date']
    list_filter = ['certificate_type', 'issue_date']
    search_fields = ['certificate_number', 'student__student_name', 'student__u_registration_no']
    fields = ['student', 'certificate_type', 'certificate_number', 'issue_date', 'purpose', 'remarks', 'issued_by']
    
    def get_student_name(self, obj):
        return obj.student.student_name
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'student__student_name'
    
    def get_registration_no(self, obj):
        return obj.student.u_registration_no
    get_registration_no.short_description = 'Registration No'
    get_registration_no.admin_order_field = 'student__u_registration_no'


from django.db import models
from django.utils import timezone

# Create your models here.

class AcademicSession(models.Model):
    session_code=models.CharField(max_length=20,unique=True)
    start_date=models.DateField()
    end_date=models.DateField()
    is_current=models.BooleanField(default=False)

    class Meta:
        db_table='session'
        ordering = ['-start_date']

    def __str__(self):
        return self.session_code

class Semester(models.Model):
    semester_number=models.IntegerField(unique=True)
    semester_name=models.CharField(max_length=50)

    class Meta:
        db_table="semesters"
        ordering=['semester_number']

    def __str__(self):
        return self.semester_name

class Subject(models.Model):
    COURSE_TYPE_CHOICES= [
        ('MAJOR', 'Major Course'),
        ('MINOR', 'Minor Course'),
        ('MD1', 'Multidisciplinary 1'),
        ('MD2', 'Multidisciplinary 2'),
        ('SKILL', 'Skill Enhancement'),
        ('VAC1', 'Value Added Course 1'),
        ('VAC2', 'Value Added Course 2'),
        ('AEC', 'Ability Enhancement Course'),
        
    ]
    subject_code=models.CharField(max_length=50,unique=True)
    subject_name=models.CharField(max_length=120)
    course_type=models.CharField(max_length=20,choices=COURSE_TYPE_CHOICES)
    
    class Meta:
        db_table="subjects"
        ordering = ['course_type', 'subject_name']

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
    


    
class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        
    ]
    
    
    # Primary identifiers (these remain constant throughout student's college life)
    reg_form_no = models.CharField(max_length=50, unique=True)
    u_registration_no = models.CharField(max_length=50, unique=True)
    class_roll_no=models.CharField(max_length=15,unique=True)
    
    # Course details (constant)
    course_name = models.CharField(max_length=200)
    batch = models.CharField(max_length=50)
    
    # Personal information
    student_name = models.CharField(max_length=200)
    parent_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Location details
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    tehsil = models.CharField(max_length=100, null=True, blank=True)
    constituency = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=100, null=True, blank=True)
    village = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField()
    community = models.CharField(max_length=50)
    
    # Contact information
    mobile = models.CharField(max_length=15)
    email_id = models.EmailField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    admission_date = models.DateField(default=timezone.now)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        ordering = ['student_name']
        indexes = [
            models.Index(fields=['u_registration_no']),
            models.Index(fields=['batch']),
        ]
    
    def __str__(self):
        return f"{self.u_registration_no} - {self.student_name}"


class StudentSemester(models.Model):
    """Records student's enrollment for each semester-session combination"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='semester_records')
    session = models.ForeignKey(AcademicSession, on_delete=models.PROTECT)
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT)
    
    
    # Subjects for this semester (can change each semester)
    major_course = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='major_enrollments')

    minor_course = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='minor_enrollments')
    md1 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='md1_enrollments')
    md2 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='md2_enrollments')
    skill = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='skill_enrollments')
    vac1 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='vac1_enrollments')
    vac2 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='vac2_enrollments')
    aec = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='aec_enrollments')
    
    # Enrollment status for this semester
    is_enrolled = models.BooleanField(default=True)
    enrollment_date = models.DateField(default=timezone.now)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_semesters'
        ordering = ['session', 'semester']
        unique_together = [['student', 'session', 'semester']]
        indexes = [
            models.Index(fields=['session', 'semester']),
            models.Index(fields=['student', 'session']),
        ]
    
    def __str__(self):
        return f"{self.student.student_name} - {self.session.session_code} - Sem {self.semester.semester_number}"


class Certificate(models.Model):
    CERTIFICATE_TYPE_CHOICES = [
        ('bonafide', 'Bonafide'),
        ('marks_sheet', 'Marks Sheet'),
        ('degree', 'Degree'),
        ('discharge_cum_character', 'Discharge cum Character'),
        ('character_not_passed', 'Character for Not Passed'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    student_semester = models.ForeignKey(StudentSemester, on_delete=models.SET_NULL, null=True, blank=True, related_name='certificates')
    certificate_type = models.CharField(max_length=50, choices=CERTIFICATE_TYPE_CHOICES)
    
    # Certificate details
    certificate_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    issue_date = models.DateField(default=timezone.now)
    
    # Additional info
    purpose = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    issued_by = models.CharField(max_length=200, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'certificates'
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['student', '-issue_date']),
            models.Index(fields=['issue_date'])
        ]
    
    def __str__(self):
        return f"{self.get_certificate_type_display()} - {self.student.student_name} - {self.issue_date}"

class StudentSubjectEnrollment(models.Model):
    student_semester = models.ForeignKey(StudentSemester, on_delete=models.CASCADE, related_name='subject_enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    
    class Meta:
        db_table = 'student_subject_enrollments'
        unique_together = [['student_semester', 'subject']]

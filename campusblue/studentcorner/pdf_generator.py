"""
Updated PDF Generator for Bonafide Certificate
Replace your existing pdf_generator.py with this file
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings

def generate_bonafide_certificate(student, certificate, student_semester=None):
    """
    Generate a bonafide certificate PDF matching the exact Word document format
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # 595.27 x 841.89 points
    
    # Set title
    p.setTitle(f"Bonafide Certificate - {student.student_name}")
    
    # ===== HEADER SECTION WITH LOGOS =====
    header_y = height - 80  # Start from top
    
    left_logo_path = os.path.join(settings.BASE_DIR, 'studentcorner', 'static', 'images', 'left_logo.png')
    right_logo_path = os.path.join(settings.BASE_DIR, 'studentcorner', 'static', 'images', 'right_logo.png') 
    # Left logo (0.75625 inch x 0.9819 inch from document)
    try:
        if os.path.exists(left_logo_path):
            p.drawImage(left_logo_path, 50, header_y, 
                       width=0.75625*inch, height=0.9819*inch, 
                       preserveAspectRatio=True, mask='auto')
    except Exception as e:
        pass  # Skip if logo not found
    
    # Right logo (0.7347 inch x 0.8736 inch from document)
    try:
        if os.path.exists(right_logo_path):
            p.drawImage(right_logo_path, width - 50 - 0.7347*inch, header_y,
                       width=0.7347*inch, height=0.8736*inch,
                       preserveAspectRatio=True, mask='auto')
    except Exception as e:
        pass  # Skip if logo not found
    
    # ===== COLLEGE HEADER TEXT (CENTER ALIGNED) =====
    text_y = height - 50
    
    # Line 1: Office of the Principal (Bold + Underlined)
    p.setFont("Helvetica-Bold", 14)
    line1 = "Office of the Principal Saqib Mohi-ud-Din Memorial"
    line1_width = p.stringWidth(line1, "Helvetica-Bold", 14)
    line1_x = (width - line1_width) / 2
    p.drawString(line1_x, text_y, line1)
    # Draw underline
    p.line(line1_x, text_y - 2, line1_x + line1_width, text_y - 2)
    
    # Line 2: College Name (Bold)
    text_y -= 20
    p.setFont("Helvetica-Bold", 13)
    line2 = "Govt. Degree College Zainapora (Shopian)"
    p.drawCentredString(width/2, text_y, line2)
    
    # Line 3: UT Of J&K (Bold)
    text_y -= 20
    p.setFont("Helvetica-Bold", 14)
    line3 = "UT Of J&K"
    p.drawCentredString(width/2, text_y, line3)
    left_margin = 70
    # Line 4: Contact Information (Bold, smaller font)
    text_y -= 20
    p.setFont("Helvetica-Bold", 9)
    line4 = "Mail: gdczainapora@gmail.com Website: www.gdczainapora.edu.in"
    p.drawCentredString(width/2, text_y, line4)
    
    # ===== CERTIFICATE NUMBER AND DATE =====
    text_y -= 30
    p.setFont("Helvetica-Bold", 12)
    
    # Certificate number (left aligned)
    current_year = datetime.now().year
    cert_no=certificate.id+100
    cert_number = f"SMMDCZ/GN/{current_year}/{cert_no:02d}"
    p.drawString(left_margin, text_y, cert_number)
    
    # Date (right aligned)
    date_str = f"Dated: {certificate.issue_date.strftime('%d-%m-%Y')}"
    date_width = p.stringWidth(date_str, "Helvetica-Bold", 12)
    p.drawRightString(width - 70, text_y, date_str)
    
    # ===== TITLE: BONAFIDE CERTIFICATE =====
    text_y -= 35
    p.setFont("Helvetica-Bold", 14)
    title = "BONAFIDE CERTIFICATE"
    p.drawCentredString(width/2, text_y, title)
    
    # ===== PHOTO PLACEHOLDER BOX (TOP RIGHT) =====
    # Position photo box in top right area
    photo_x = width - 150  # 150 points from right edge
    photo_y = text_y - 20  # Below the title
    body_y=text_y-70
    photo_width = 1.2 * inch
    photo_height = 1.5 * inch
    
    # Draw photo box
    p.setLineWidth(1)
    p.rect(photo_x, photo_y - photo_height, photo_width, photo_height, stroke=1, fill=0)
    
    # Add "Affix Photograph Here" text inside box
    p.setFont("Helvetica", 8)
    p.drawCentredString(photo_x + photo_width/2, photo_y - photo_height/2 + 10, "Affix")
    p.drawCentredString(photo_x + photo_width/2, photo_y - photo_height/2 - 5, "Photograph")
    p.drawCentredString(photo_x + photo_width/2, photo_y - photo_height/2 - 20, "Here")
    
 # ===== CERTIFICATE BODY =====
    body_y = text_y - 40
    left_margin = 70  # Define left margin here
    line_spacing = 22
    
    # Line 1: "This is certified that"
    p.setFont("Helvetica", 14)
    line1 = "This is certified that "
    line1_width = p.stringWidth(line1, "Helvetica", 14)
    p.drawString(left_margin, body_y, line1)
    
    # Student name (centered on underline)
    underline_length = 200  # Fixed length underline
    name_x = left_margin + line1_width
    
    p.setFont("Helvetica-Bold", 14)
    student_name = student.student_name.upper()
    name_width = p.stringWidth(student_name, "Helvetica-Bold", 14)
    
    # Center the name on the underline
    name_center_x = name_x + (underline_length - name_width) / 2
    p.drawString(name_center_x, body_y, student_name)
    
    # Draw underline
    p.line(name_x, body_y - 2, name_x + underline_length, body_y - 2)
    
    # Line 2: S.O/D.O
    body_y -= line_spacing
    p.setFont("Helvetica", 14)
    relation = "S.O" if student.gender == 'M' else "D.O"
    line2 = f"{relation} "
    line2_width = p.stringWidth(line2, "Helvetica", 14)
    p.drawString(left_margin, body_y, line2)
    
    # Parent name (centered on underline)
    parent_x = left_margin + line2_width
    p.setFont("Helvetica-Bold", 14)
    parent_name = student.parent_name.upper()
    parent_width = p.stringWidth(parent_name, "Helvetica-Bold", 14)
    
    # Center the parent name on the underline
    parent_center_x = parent_x + (underline_length - parent_width) / 2
    p.drawString(parent_center_x, body_y, parent_name)
    
    # Underline for parent name
    p.line(parent_x, body_y - 2, parent_x + underline_length, body_y - 2)
    
    # Continue same line: "is currently enrolled in"
    body_y -= line_spacing
    p.setFont("Helvetica", 14)
    p.drawString(left_margin, body_y, "is currently enrolled in")
    
    # Line 3: UG [Semester] Semester
    body_y -= line_spacing
    p.setFont("Helvetica", 14)
    ug_text = "UG "
    ug_width = p.stringWidth(ug_text, "Helvetica", 14)
    p.drawString(left_margin, body_y, ug_text)
    
    # Semester (centered on underline)
    sem_x = left_margin + ug_width
    underline_sem_length = 100
    
    if student_semester:
        semester_name = student_semester.semester.semester_name
    else:
        semester_name = "_____________"
    
    p.setFont("Helvetica-Bold", 14)
    sem_width = p.stringWidth(semester_name, "Helvetica-Bold", 14)
    
    # Center semester on underline
    sem_center_x = sem_x + (underline_sem_length - sem_width) / 2
    p.drawString(sem_center_x, body_y, semester_name)
    p.line(sem_x, body_y - 2, sem_x + underline_sem_length, body_y - 2)
    
    # "Semester in this college for the"
    p.setFont("Helvetica", 14)
    remaining_text = " Semester in this college for the"
    p.drawString(sem_x + underline_sem_length + 5, body_y, remaining_text)
    
    # Line 4: Year
    body_y -= line_spacing
    p.setFont("Helvetica", 14)
    year_label = "Year "
    year_width = p.stringWidth(year_label, "Helvetica", 14)
    p.drawString(left_margin, body_y, year_label)
    
    # Academic year (centered on underline) - Always use current year
    year_x = left_margin + year_width
    underline_year_length = 150
    
    current_year = datetime.now().year
    session_name = str(current_year)
    
    p.setFont("Helvetica-Bold", 14)
    year_str_width = p.stringWidth(session_name, "Helvetica-Bold", 14)
    
    # Center year on underline
    year_center_x = year_x + (underline_year_length - year_str_width) / 2
    p.drawString(year_center_x, body_y, session_name)
    p.line(year_x, body_y - 2, year_x + underline_year_length, body_y - 2)
    
    # Line 5: Batch
    body_y -= line_spacing
    p.setFont("Helvetica", 14)
    batch_label = "Batch "
    batch_width = p.stringWidth(batch_label, "Helvetica", 14)
    p.drawString(left_margin, body_y, batch_label)
    
    # Batch (centered on underline)
    batch_x = left_margin + batch_width
    underline_batch_length = 120
    
    p.setFont("Helvetica-Bold", 14)
    batch_str = student.batch
    batch_str_width = p.stringWidth(batch_str, "Helvetica-Bold", 14)
    
    # Center batch on underline
    batch_center_x = batch_x + (underline_batch_length - batch_str_width) / 2
    p.drawString(batch_center_x, body_y, batch_str)
    p.line(batch_x, body_y - 2, batch_x + underline_batch_length, body_y - 2)
    
    # Line 6: Class Roll No
    body_y -= line_spacing
    p.setFont("Helvetica", 14)
    roll_label = "Class Roll.No. "
    roll_width = p.stringWidth(roll_label, "Helvetica", 14)
    p.drawString(left_margin, body_y, roll_label)
    
    # Class Roll No (centered on underline)
    roll_x = left_margin + roll_width
    underline_roll_length = 120
    
    p.setFont("Helvetica-Bold", 14)
    roll_str = student.class_roll_no
    roll_str_width = p.stringWidth(roll_str, "Helvetica-Bold", 14)
    
    # Center roll number on underline
    roll_center_x = roll_x + (underline_roll_length - roll_str_width) / 2
    p.drawString(roll_center_x, body_y, roll_str)
    p.line(roll_x, body_y - 2, roll_x + underline_roll_length, body_y - 2)
    
    # Line 7: Registration No (only if available)
    if student.u_registration_no and student.u_registration_no.strip():
        body_y -= line_spacing
        p.setFont("Helvetica", 14)
        reg_label = "Registration No. "
        reg_width = p.stringWidth(reg_label, "Helvetica", 14)
        p.drawString(left_margin, body_y, reg_label)
        
        # Registration No (centered on underline)
        reg_x = left_margin + reg_width
        underline_reg_length = 150
        
        p.setFont("Helvetica-Bold", 14)
        reg_str = student.u_registration_no
        reg_str_width = p.stringWidth(reg_str, "Helvetica-Bold", 14)
        
        # Center registration number on underline
        reg_center_x = reg_x + (underline_reg_length - reg_str_width) / 2
        p.drawString(reg_center_x, body_y, reg_str)
        p.line(reg_x, body_y - 2, reg_x + underline_reg_length, body_y - 2)
    # Line 8: Course
    body_y -= line_spacing
    p.setFont("Helvetica", 14)
    course_label = "Course: "
    course_width = p.stringWidth(course_label, "Helvetica", 14)
    p.drawString(left_margin, body_y, course_label)
    
    course_x = left_margin + course_width
    p.setFont("Helvetica-Bold", 14)
    p.drawString(course_x, body_y, student.course_name)
    
    # ===== DATE AND SIGNATURE =====
    body_y -= 60
    
    # Date
    p.setFont("Helvetica", 14)
    date_label = "Dated: "
    date_width = p.stringWidth(date_label, "Helvetica", 14)
    p.drawString(left_margin, body_y, date_label)
    
    # Date (centered on underline)
    date_x = left_margin + date_width
    underline_date_length = 100
    
    p.setFont("Helvetica-Bold", 14)
    date_str_value = certificate.issue_date.strftime('%d/%m/%Y')
    date_str_width = p.stringWidth(date_str_value, "Helvetica-Bold", 12)
    
    # Center date on underline
    date_center_x = date_x + (underline_date_length - date_str_width) / 2
    p.drawString(date_center_x, body_y, date_str_value)
    p.line(date_x, body_y - 2, date_x + underline_date_length, body_y - 2)
    
    # Principal signature (right side)
    signature_y = body_y - 120
    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(width - left_margin, signature_y, "Principal")
    # Line for signature
    # p.line(width - left_margin - 150, signature_y + 20, width - left_margin, signature_y + 20)
    
    # ===== FOOTER =====
    p.setFont("Helvetica", 7)
    p.setFillColorRGB(0.6, 0.6, 0.6)
    footer_text = f"Generated on {datetime.now().strftime('%d-%m-%Y at %I:%M %p')}"
    p.drawCentredString(width/2, 30, footer_text)
    
    # Save
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
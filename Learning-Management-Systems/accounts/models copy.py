from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings

from django.db.models import Q
from PIL import Image

from course.models import Program
from .validators import ASCIIUsernameValidator
from course.models import Program, Course
from django.core.exceptions import ValidationError
import os
from PIL import Image


# Level Choices
Open = "Open"
Basic = "Basic"
Intermediate = "Intermediate"
Advance = "Advance"

LEVEL = (
    (Open, "Open"),
    (Basic, "Basic"),
    (Intermediate, "Intermediate"),
    (Advance, "Advance"),
)

# Department Choices
DEPARTMENT = (
    ("CTM-HO", "CTM-HO"),
    ("HR", "HR"),
    ("Accounts_Finance", "Accounts_Finance"),
    ("Stores", "Stores"),
    ("WDL", "WDL"),
    ("Line_1_3", "Line_1_3"),
    ("Coating_Line", "Coating_Line"),
    ("Customer Sales Support", "Customer Sales Support"),
    ("Taxation", "Taxation"),
    ("Commercial", "Commercial"),
    ("Warehouse_Logistics", "Warehouse_Logistics"),
    ("Quality_Control", "Quality_Control"),
    ("Corporate_Sales", "Corporate_Sales"),
    ("Project Sales", "Project Sales"),
    ("Mechanical", "Mechanical"),
    ("Line_2", "Line_2"),
    ("Administration", "Administration"),
    ("Dispatch", "Dispatch"),
    ("PPC", "PPC"),
    ("SCM", "SCM"),
    ("Accounts", "Accounts"),
    ("Sampling", "Sampling"),
    ("Electrical", "Electrical"),
    ("Export", "Export"),
    ("Trade_Marketing", "Trade_Marketing"),
    ("CTM-Operations", "CTM-Operations"),
    ("CTM-Sales", "CTM-Sales"),
    ("PT_Operator", "PT_Operator"),
    ("Rewinding_Operator", "Rewinding_Operator"),
    ("Procurement", "Procurement"),
    ("Line_4_5", "Line_4_5"),
    ("Research_Development", "Research_Development"),
    ("Legal", "Legal"),
    ("FR_Production", "FR_Production"),
    ("Coordination", "Coordination"),
    ("IT", "IT"),
    ("Technical_Support", "Technical_Support"),
    ("Design_Application", "Design_Application"),
    ("HoneyComb1", "HoneyComb1"),
    ("Management Information System", "Management Information System"),
    ("Operations", "Operations"),
    ("Data Management Executive", "Data Management Executive"),
    ("Quality_Assurance", "Quality_Assurance"),
    ("Enterprise_Technology", "Enterprise_Technology"),
    ("Lab", "Lab"),
    ("Project Sales_Product Specification", "Project Sales_Product Specification"),
    ("Audit", "Audit"),
    ("Process Coordinator", "Process Coordinator"),
    ("Virtual Sales", "Virtual Sales"),
    ("Management", "Management"),
    ("System Developments & Automation", "System Developments & Automation"),
    ("Business Management System", "Business Management System"),
    ("CRM Application Management", "CRM Application Management"),
    ("CSS_CBD of CSS", "CSS_CBD of CSS"),
    ("Project Sales_Spec_BD_KAM", "Project Sales_Spec_BD_KAM"),
    ("CRM", "CRM"),
    ("MIS", "MIS"),
    ("EXIM", "EXIM"),
    ("SAP", "SAP"),
    ("Product Specification", "Product Specification"),
    ("Zinc Series", "Zinc Series"),
    ("L&D", "L&D"),
    ("Online_Quality", "Online_Quality"),
    ("Marketing", "Marketing"),
    ("Digital Marketing", "Digital Marketing"),
    ("Customer Business Development of CSS", "Customer Business Development of CSS"),
    ("Brand Activation", "Brand Activation"),
    ("Design_Execution", "Design_Execution"),
    ("Customer Sales Support_Customer Business Development of CSS", "Customer Sales Support_Customer Business Development of CSS"),
    ("Marcom", "Marcom"),
    ("Billing", "Billing"),
    ("Zinc_Solid_Panel", "Zinc_Solid_Panel"),
    ("Line_6", "Line_6"),
    ("Tinting", "Tinting"),
    ("BD/KAM", "BD/KAM"),
    ("Operation_Trainee", "Operation_Trainee"),
    ("Lean", "Lean"),
    ("ACP_LOUVERS", "ACP_LOUVERS"),
    ("Business Strategy_Operation", "Business Strategy_Operation"),
)

# Zone Choices
ZONE = (
    ("Corporate", "Corporate"),
    ("Haridwar", "Haridwar"),
    ("East", "East"),
    ("North", "North"),
    ("South", "South"),
    ("West", "West"),
    ("South & West", "South & West"),
    ("Upper_North", "Upper_North"),
)

# Branch Choices
BRANCH = (
    ("Head Office", "Head Office"),
    ("Unit-I", "Unit-I"),
    ("Unit-I&II&III", "Unit-I&II&III"),
    ("CMDO", "CMDO"),
    ("Unit-II", "Unit-II"),
    ("Unit-III", "Unit-III"),
    ("Kolkata", "Kolkata"),
    ("Delhi", "Delhi"),
    ("Chennai", "Chennai"),
    ("Mumbai", "Mumbai"),
    ("Ahmedabad", "Ahmedabad"),
    ("Hyderabad", "Hyderabad"),
    ("Bangalore", "Bangalore"),
    ("Cochin", "Cochin"),
    ("Unit-I & II", "Unit-I & II"),
    ("MDO", "MDO"),
    ("Pune", "Pune"),
    ("Jaipur", "Jaipur"),
    ("Indore", "Indore"),
    ("Lucknow", "Lucknow"),
    ("Bhiwandi", "Bhiwandi"),
    ("head Office", "head Office"),
    ("Calicut", "Calicut"),
)

class UserManager(UserManager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(username__icontains=query) | 
                         Q(first_name__icontains=query)| 
                         Q(last_name__icontains=query)| 
                         Q(email__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs




class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    is_dep_head = models.BooleanField(default=False)
    phone = models.CharField(max_length=60, blank=True, null=True)
    zone = models.CharField(max_length=20, choices=ZONE, default="North")  # Replaced address with zone
    branch = models.CharField(max_length=50, choices=BRANCH, default="Head Office")  # Added branch dropdown
    department = models.CharField(max_length=100, choices=DEPARTMENT, default="CTM-HO")  # Increased max_length for department dropdown
    date_of_join_in_aludecor = models.DateField(null=True, blank=True)  # Added date of join in Aludecor
    picture = models.ImageField(upload_to='profile_pictures/%y/%m/%d/', default='default.png', null=True)
    email = models.EmailField(blank=True, null=True)
    reporting_to = models.CharField(max_length=60, null=True, blank=True)


    username_validator = ASCIIUsernameValidator()

    objects = UserManager()

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    def __str__(self):
        return '{} ({})'.format(self.username, self.get_full_name)

    @property
    def get_user_role(self):
        if self.is_superuser:
            return "Admin"
        elif self.is_student:
            return "Aludecorian"
        elif self.is_lecturer:
            return "Trainer"
        elif self.is_dep_head:
            return "Head of the Department"

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + 'default.png'
            return no_picture

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_pics')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        try:
            img = Image.open(self.picture.path)
            
            # Set the maximum allowed size to 3KB
            max_size_kb = 3 * 1024  # 3KB in bytes
            
            # Start with a lower quality and compress until it meets the size limit
            quality = 70

            while os.path.getsize(self.picture.path) > max_size_kb and quality > 10:
                img.save(self.picture.path, optimize=True, quality=quality)
                quality -= 5  # Reduce quality each loop to decrease size

            if os.path.getsize(self.picture.path) > max_size_kb:
                raise ValueError("Could not compress the image to be less than 3KB")

        except Exception as e:
            print(f"Error in processing image: {e}")
            pass


    

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + 'default.png':
            self.picture.delete()
        super().delete(*args, **kwargs)


class StudentManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(level__icontains=query) | 
                         Q(department__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, null=True)
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    objects = StudentManager()

    def __str__(self):
        return self.student.get_full_name

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})
    
    class Meta:
        ordering = ['id']

    def delete(self, *args, **kwargs):
        self.student.delete()
        super().delete(*args, **kwargs)


class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    course = models.CharField(max_length=50,  null=True)

    def __str__(self):
        return "{}".format(self.user)
    
class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return "{}".format(self.user.get_full_name)
    

class learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    course = models.CharField(max_length=50,  null=True)

    def __str__(self):
        return "{}".format(self.user)
    

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_save
from django.db.models import Q




# project import
from .utils import *

VERTICAL = (
    ('All', 'All'),
        ('Unit', 'Unit'),
        ('Branch', 'Branch'),

    )

# LEVEL_COURSE = "Level course"
OPEN = "Open Soft Skill"
BASIC = "Basic-Techical Skill"
INTERMEDIATE = "Intermediate-Techical Skill"
ADVANCE = "Advance-Techical Skill"
OPEN = "Open Soft Skill"
BASIC = "Basic-Soft Skill"
INTERMEDIATE = "Intermediate-Soft Skill"
ADVANCE = "Advance-Soft Skill"
LEVEL = (
    # (LEVEL_COURSE, "Level course"),
    (OPEN, "Open-Techical Skill"),
    (BASIC, "Basic-Techical Skill"),
    (INTERMEDIATE, "Intermediate-Techical Skill"),
    (ADVANCE, "Advance-Techical Skill"),
    (OPEN, "Open-Soft Skill"),
    (BASIC, "Basic-Soft Skill"),
    (INTERMEDIATE, "Intermediate-Soft Skill"),
    (ADVANCE, "Advance-Soft Skill"),


)

HINDI = "Hindi"
ENGLISH = "English"
REGIONAL = "Regional"

LANGUAGE = (
    (HINDI, "Hindi"),
    (ENGLISH, "English"),
    (REGIONAL, "Regional"),
)




CATEGORY_CHOICES = (
    ('Soft Skill', 'Soft Skill'),
        ('Technical Skill', 'Technical Skill')
        
    )

class ProgramManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(title__icontains=query) | 
                         Q(summary__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class Program(models.Model):
    title = models.CharField(max_length=150, unique=True)
    # summary = models.TextField(null=True, blank=True)
    summary = models.CharField(max_length=100, choices=CATEGORY_CHOICES,default='null')

    objects = ProgramManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('program_detail', kwargs={'pk': self.pk})


class CourseManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(title__icontains=query) | 
                         Q(summary__icontains=query)| 
                         Q(code__icontains=query)| 
                         Q(slug__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class Course(models.Model):
    slug = models.SlugField(blank=True, unique=True)
    title = models.CharField(max_length=200, null=True)
    code = models.CharField(max_length=200, unique=True, null=True)
    credit = models.IntegerField(null=True, default=0)
    summary = models.TextField(max_length=200, blank=True, null=True)
    # summary = models.CharField(max_length=100, choices=CATEGORY_CHOICES,default='null')

    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    level = models.CharField(max_length=50, choices=LEVEL, null=True)
    vertical = models.CharField(max_length=25,choices=VERTICAL, null=True)
    language = models.CharField(choices=LANGUAGE, max_length=200)
    is_elective = models.BooleanField(default=False, blank=True, null=True)
    # program_id = models.IntegerField(null=True, default=0)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    

    objects = CourseManager()

    def __str__(self):
        return "{0} ({1})".format(self.title, self.code)

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})
    
    @property
    def is_current_semester(self):
        from app.models import Semester
        current_semester = Semester.objects.get(is_current_semester=True)

        if self.semester == current_semester.semester:
            return True
        else:
            return False

def course_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(course_pre_save_receiver, sender=Course)


class CourseAllocation(models.Model):
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='allocated_lecturer')
    courses = models.ManyToManyField(Course, related_name='allocated_course')
    session = models.ForeignKey("app.Session", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.lecturer.get_full_name

    def get_absolute_url(self):
        return reverse('edit_allocated_course', kwargs={'pk': self.pk})


class Upload(models.Model):
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.CharField(max_length=50)
    # file = models.FileField(upload_to='course_files/', validators=[FileExtensionValidator(['pdf', 'docx', 'doc', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', '7zip'])])
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    def __str__(self):
        return str(self.file)[6:]

    # def get_extension_short(self):
    #     ext = str(self.file).split(".")
    #     ext = ext[len(ext)]
    #     if ext == 'doc' or ext == 'docx':
    #         return 'word'
    #     elif ext == 'pdf':
    #         return 'pdf'
    #     elif ext == 'xls' or ext == 'xlsx':
    #         return 'excel'
    #     elif ext == 'zip' or ext == 'rar' or ext == 'zip':
    #         return 'archive'

    # def delete(self, *args, **kwargs):
    #     self.file.delete()
    #     super().delete(*args, **kwargs)
def delete(self, *args, **kwargs):
    # Check the type of self.video
    print(type(self.video), self.video)

    if hasattr(self.video, 'delete'):
        self.video.delete()
    else:
        print("self.video is not a file-like object. It's a string:", self.video)

    super().delete(*args, **kwargs)


class UploadVideo(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, unique=True,max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.CharField(max_length=100)
    # video = models.FileField(upload_to='course_videos/', validators=[FileExtensionValidator(['mp4', 'mkv', 'wmv', '3gp', 'f4v', 'avi', 'mp3'])])
    summary = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('video_single', kwargs={'slug': self.course.slug, 'video_slug': self.slug})





    def delete(self, *args, **kwargs):
        self.video.delete()
        super().delete(*args, **kwargs)


def video_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(video_pre_save_receiver, sender=UploadVideo)


class CourseOffer(models.Model):
	"""NOTE: Only department head can offer semester courses"""
	dep_head = models.ForeignKey("accounts.DepartmentHead", on_delete=models.CASCADE)

	def __str__(self):
		return "{}".format(self.dep_head)



class CourseAllocationLearner(models.Model):
    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)    
    courses = models.ManyToManyField(Course, related_name='learner_course_allocations')
    session = models.ForeignKey("app.Session", on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    def __str__(self):
        return self.student.get_full_name

    def get_absolute_url(self):
        return reverse('edit_allocated_course', kwargs={'pk': self.pk})
    



class CourseRequest(models.Model):
    REQUEST_STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    hod = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hod_requests',
        help_text="HOD making the request"
    )
    team_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_member_requests',
        help_text="Team member for whom the request is being made"
    )
    program = models.ForeignKey(Program, on_delete=models.CASCADE, help_text="Selected program")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, help_text="Selected course")
    level = models.CharField(max_length=50, help_text="Skill level for the course")
    department = models.CharField(max_length=255, help_text="Department of the team member")
    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS,
        default='Pending',
        help_text="Approval status of the request"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Request creation timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Request update timestamp")

    def __str__(self):
        # Safeguard against null or missing data
        course_title = self.course.title if self.course else "Unknown Course"
        team_member_name = (
            f"{self.team_member.first_name} {self.team_member.last_name}"
            if self.team_member else "Unknown Team Member"
        )
        return f"{course_title} ({self.status}) for {team_member_name}"
    
   

    
 
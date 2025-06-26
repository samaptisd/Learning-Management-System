from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, Student,DepartmentHead
from django.contrib.auth.models import AbstractUser
from django.db import models



class UserAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'username', 'email', 'is_active', 'is_student', 'is_lecturer' , 'is_staff','is_dep_head']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_lecturer', 'is_staff','is_dep_head']

    class Meta:
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class ScoreAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'course', 'assignment', 'mid_exam', 'quiz',
        'attendance', 'final_exam', 'total', 'grade', 'comment'
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Student)
admin.site.register(DepartmentHead)


# admin.site.unregister(Group)


from django.contrib import admin
from .models import UserActivityLog

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'url', 'method', 'start_time', 'end_time', 'duration']
    list_filter = ['user', 'action', 'start_time', 'method']
    search_fields = ['user__username', 'url']


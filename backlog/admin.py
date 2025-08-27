from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, TeamMember, Task, TaskStatusHistory

# Custom User Admin
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role', 'google_id')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')

# Project Admin
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'created_by', 'created_at')
    list_filter = ('manager',)
    search_fields = ('name', 'description')

# TeamMember Admin
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('member', 'project')
    list_filter = ('project',)
    search_fields = ('member__username', 'project__name')

# Task Admin
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'assigned_to', 'created_by', 'created_at')
    list_filter = ('status', 'project')
    search_fields = ('title', 'description')


admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Task, TaskAdmin)

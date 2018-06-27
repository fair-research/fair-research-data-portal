from django.contrib import admin

from globus_portal_framework.search.models import Minid

from portal.models import Task, Workflow, Profile


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_workflow', 'status', 'user')

    def get_workflow(self, obj):
        return obj.name

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

from django.contrib import admin

from globus_portal_framework.search.models import Minid

from portal.models import Task, Workflow, Profile


@admin.register(Task, Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

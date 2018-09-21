from django.contrib import admin

from globus_portal_framework.search.models import Minid

from portal.models import Task, Workspace, Profile


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'date_added')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_workspace', 'status', 'user')

    def get_workspace(self, obj):
        return obj.workspace.name


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

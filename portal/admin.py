from django.contrib import admin

from globus_portal_framework.search.models import Minid

from portal.models import Workflow


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

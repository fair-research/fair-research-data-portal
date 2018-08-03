from django.urls import path, include, re_path, reverse
from django.shortcuts import redirect
from django.contrib import admin
from django.conf import settings


from portal.views import (intro_page, bag_create, workflows, tasks,
                          bag_delete, bag_add, workflow_delete, profile,
                          task_detail)

from portal.api import task_start, update_tasks



apipatterns = [
    path('task/start/', task_start, name='task-start'),
    path('tasks/update/', update_tasks, name='tasks-update'),
    # path('tasks/active', get_running_tasks, name='tasks-active')
]

general = [
    path('', intro_page, name='intro-page'),
    path('admin/', admin.site.urls),
    path('profile/', profile, name='profile'),
    path('bags/', workflows, name='bag-list'),
    path('workspaces/', workflows, name='workspaces'),
    path('workflows/', lambda x: redirect(reverse('workspaces')),
         name='workflows'),
    path('bags/create/', bag_create, name='bag-create'),

    # path('search/bags/create/', bag_create, name='bag-create'),
    path('workflow/delete', workflow_delete, name='workflow-delete'),
    path('task/<int:task>/', task_detail, name='task'),
    path('tasks', tasks, name='tasks'),
    path('search/bags/delete/<path:minid>/', bag_delete, name='bag-delete'),
    path('search/bags/add', bag_add, name='bag-add'),
    # path('search/', include('globus_portal_framework.search.urls')),


    # path('', landing_page, name='landing_page')
]

urlpatterns = [
    path('', include('social_django.urls')),
    path('', include('django.contrib.auth.urls')),
    # path()
    path('' + 'api/v1/', include(apipatterns)),
    path('', include(general)),
    path('search/', include('globus_portal_framework.search.urls'),
         name='landing_page'),

]

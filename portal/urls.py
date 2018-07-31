from django.urls import path, include, re_path
from django.contrib import admin


from portal.views import (landing_page, bag_create, workflows, tasks,
                          bag_delete, bag_add, workflow_delete, profile,
                          task_detail, collect_minids, task_delete)

from portal.api import task_start, update_tasks

apipatterns = [
    path('task/start/', task_start, name='task-start'),
    path('tasks/update/', update_tasks, name='tasks-update'),
    # path('tasks/active', get_running_tasks, name='tasks-active')
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls')),
    path('', include('django.contrib.auth.urls')),
    path('api/v1/', include(apipatterns)),
    path('profile/', profile, name='profile'),
    path('bags/', workflows, name='bag-list'),
    path('workflows', workflows, name='workflows'),
    path('bags/create/', bag_create, name='bag-create'),
    path('collect-minids', collect_minids, name='collect-minids'),
    # path('search/bags/create/', bag_create, name='bag-create'),
    path('workflow/delete', workflow_delete, name='workflow-delete'),
    path('task/<int:task>/', task_detail, name='task'),
    path('task', tasks, name='tasks'),
    path('task/delete', task_delete, name='task-delete'),

    path('search/bags/delete/<path:minid>/', bag_delete, name='bag-delete'),
    path('search/bags/add', bag_add, name='bag-add'),
    path('search/', include('globus_portal_framework.search.urls')),

    path('', include('globus_portal_framework.search.urls'), name='landing_page')
    # path('', landing_page, name='landing_page')
]

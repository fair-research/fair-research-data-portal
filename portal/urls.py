from django.urls import path, include, re_path, reverse
from django.contrib import admin
from django.conf import settings
from django.shortcuts import redirect

from portal.views import (intro_page, landing_page, bag_create, workspaces,
                          tasks, bag_delete, bag_add, workspace_delete,
                          profile, task_detail, collect_minids, task_delete)

from portal.api import task_start, update_tasks
from api.urls import urlpatterns as api_urlpatterns

apipatterns = [
    path('task/start/', task_start, name='task-start'),
    path('tasks/update/', update_tasks, name='old-tasks-update'),
    # path('tasks/active', get_running_tasks, name='tasks-active')
]

main_site = [
    path('' if settings.SERVER_URL else 'intro', intro_page, name='intro-page'),
    path('admin/', admin.site.urls),
    path('', include('social_django.urls')),
    path('', include('django.contrib.auth.urls')),
    path('api/v1/', include(apipatterns)),
    path('api/v1/', include(api_urlpatterns)),
    path('profile/', profile, name='profile'),
    path('bags/', workspaces, name='bag-list'),
    path('workspaces/', workspaces, name='workspaces'),
    path('workspaces/', lambda r: redirect(reverse('workspaces')),
         name='workspaces'),
    path('bags/create/', bag_create, name='bag-create'),
    path('collect-minids', collect_minids, name='collect-minids'),
    # path('search/bags/create/', bag_create, name='bag-create'),
    path('workspace/delete', workspace_delete, name='workspace-delete'),
    path('task/<int:task>/', task_detail, name='task'),
    path('task', tasks, name='tasks'),
    path('task/delete', task_delete, name='task-delete'),

    path('search/bags/delete/<path:minid>/', bag_delete, name='bag-delete'),
    path('search/bags/add', bag_add, name='bag-add'),
    path('search/', include('globus_portal_framework.search.urls')),

]

# I can't get this thing working properly the right way, make it work!
base_workspace_redirect_url = ('/4M.4.Fullstacks/login/globus?next='
                               '/4M.4.Fullstacks/workspaces/')

urlpatterns = [
    path('', landing_page, name='landing-page'),
    #path('search', include('globus_portal_framework.search.urls'), name='landing-page')
    # path('', landing_page, name='landing_page')
    path(settings.SERVER_URL, include(main_site)),
    path('workspaces/', lambda r: redirect(base_workspace_redirect_url)),
    path('search/', lambda r: redirect(reverse('search'))),
]

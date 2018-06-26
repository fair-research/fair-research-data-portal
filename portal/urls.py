from django.urls import path, include, re_path
from django.contrib import admin

from portal.views import (landing_page, bag_create, workflows, tasks,
                          bag_delete, bag_add, workflow_delete, profile)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls')),
    path('', include('django.contrib.auth.urls')),
    path('profile/', profile, name='profile'),
    path('workflows', workflows, name='workflows'),
    path('workflow/delete', workflow_delete, name='workflow-delete'),
    path('tasks', tasks, name='tasks'),
    path('search/bags/create/', bag_create, name='bag-create'),
    path('search/bags/delete/<path:minid>/', bag_delete, name='bag-delete'),
    path('search/bags/add', bag_add, name='bag-add'),
    path('search/', include('globus_portal_framework.search.urls')),

    path('', include('globus_portal_framework.search.urls'), name='landing_page')
    # path('', landing_page, name='landing_page')
]

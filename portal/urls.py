from django.urls import path, include, re_path
from django.contrib import admin

from portal.views import landing_page, bag_create, workflows, tasks

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls')),
    path('', include('django.contrib.auth.urls')),
    path('workflows', workflows, name='workflows'),
    path('tasks', tasks, name='tasks'),
    path('search/bags/create/', bag_create, name='bag-create'),
    path('search/', include('globus_portal_framework.search.urls')),

    path('', landing_page, name='landing_page')
]

from django.urls import path, include

from portal.views import landing_page

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('social_django.urls')),
    path('', include('django.contrib.auth.urls')),

    path('search', include('globus_portal_framework.search.urls')),

    path('', landing_page, name='landing_page')
]

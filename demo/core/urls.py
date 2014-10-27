from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from main.views import Main, DeleteEmail, Profile, SetPrimaryEmail, DeleteUser
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', Main.as_view(), {}, 'main'),
    url(r'^profile/$', login_required(Profile.as_view(), login_url='/'),
        name='profile'),
    url(r'^mail/', include('multimail.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'},
        name='logout'),
    url(r'^delete-email/(\d+)', DeleteEmail.as_view(), name='delete-email'),
    url(r'^delete-user/([^/]+)', DeleteUser.as_view(), name='delete-user'),
    url(r'^set-primary/(\d+)', SetPrimaryEmail.as_view(), name='set-primary'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

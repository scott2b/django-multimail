from django.conf.urls import url
try:
    from django.conf.urls import patterns
except ImportError:
    from django.conf.urls.defaults import patterns
from multimail.views import Verify, SendLink

urlpatterns = patterns('',
    url(r'^verify/(\d+)/(.+)/$', Verify.as_view(), {}, name='email-verification-url'),
    url(r'^send-verification-link/(\d+)/$', SendLink.as_view(), {}, name='send-verification-link'),
    url(r'^set-as-primary/(\d+)/$', 'multimail.views.set_as_primary',
        name='set_as_primary'),
)

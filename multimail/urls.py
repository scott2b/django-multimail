from django.conf.urls.defaults import *
from multimail.views import Verify, SendLink

urlpatterns = patterns('',
    (r'^verify/(\d+)/(.+)/$', Verify.as_view(), {}, 'email-verification-url'),
    (r'^send-verification-link/(\d+)/$', SendLink.as_view(), {}, 'send-verification-link'),
)

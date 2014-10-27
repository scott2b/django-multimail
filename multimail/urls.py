from django.conf.urls import url, patterns
from multimail.views import Verify, SendLink

urlpatterns = patterns('',
    url(r'^verify/(\d+)/(.+)/$', Verify.as_view(), {},
        name='email-verification-url'),
    url(r'^send-verification-link/(\d+)/$', SendLink.as_view(), {},
        name='send-verification-link'),
    url(r'^set-as-primary/(\d+)/$', 'multimail.views.set_as_primary',
        name='set_as_primary'),
    url(r'^delete-email/(\d+)/$', 'multimail.views.delete_email',
        name='delete_email'),
)

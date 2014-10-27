from multimail.models import EmailAddress
from multimail.views import Verify
from multimail.settings import MM
from multimail.util import get_site
from mock import Mock, patch
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.test.client import RequestFactory
from django.test import TestCase
import django, multimail, unittest

try:
    from django.utils import timezone
    now = lambda: timezone.now()
except ImportError:
    import datetime
    now = lambda: datetime.datetime.now()


class EmailAddressTest(TestCase):

    def setUp(self):
        u = User(username='testuser')
        u.save()
        self.obj_ut = EmailAddress(user=u, email='testemail')
        self.obj_ut.save()

    def tearDown(self):
        User.objects.filter(username='testuser').delete()

    def test_is_verified(self):
        addr = EmailAddress()
        self.assertFalse(addr.is_verified())
        addr.verified_at = now()
        self.assertTrue(addr.is_verified())

    @patch.object(multimail.models.EmailAddress, 'send_verification')
    def test_save(self, mock_send_verification):
        addr = self.obj_ut
        self.assertEquals(40, len(addr.verif_key))
        addr.save()
        self.assertTrue(mock_send_verification.not_called)
        addr2 = EmailAddress(user=addr.user, email='testemail2')
        addr2.save()
        self.assertTrue(mock_send_verification.called)

    @patch.object(EmailMultiAlternatives, 'send')
    def test_send_verification(self, mock_send):
        addr = self.obj_ut
        addr.send_verification()
        self.assertTrue(mock_send.called)

    @patch.object(EmailMultiAlternatives, 'send')
    @patch.object(django.contrib.sites.models, 'Site')
    def test_unconfigured_site(self, mock_site,
            mock_send):
        addr = self.obj_ut
        addr.send_verification()
        mock_send.assert_called_with(fail_silently=False)
        assert not mock_site.called

    def test_get_site__MM_configs(self):
        MM.SITE_DOMAIN = 'testdomain'
        MM.SITE_NAME = 'TestName'
        site = get_site()
        self.assertEqual(site.domain, 'testdomain')        
        MM.SITE_DOMAIN = None
        MM.SITE_NAME = None
        
    def test_get_site__fallback(self):
        Site.objects.all().delete()
        Site.objects.clear_cache()
        site = get_site()
        self.assertEqual(site.domain, 'example.com')        

    def test_get_site__configured(self):
        Site.objects.all().delete()
        Site(domain='testdomain', name='TestName', id=1).save()
        settings.SITE_ID = 1
        Site.objects.clear_cache()
        site = get_site()
        self.assertEqual(site.domain, 'testdomain')        




class VerifyTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/verify')
        u = User(username='testuser')
        u.set_password('testpassword')
        u.save()
        u = authenticate(username='testuser', password='testpassword')
        self.addr = EmailAddress(user=u, email='testemail')
        self.addr.save()

    def tearDown(self):
        User.objects.filter(username='testuser').delete()

    @patch.object(django.contrib.messages, 'success')
    def test_verify__success(self, mock_success):
        response = Verify.as_view()(self.request, self.addr.pk,
            self.addr.verif_key)
        self.assertTrue(mock_success.called)

    @patch.object(django.contrib.messages, 'error')
    def test_verify__not_exist(self, mock_error):
        response = Verify.as_view()(self.request, -1, self.addr.verif_key)
        self.assertTrue(mock_error.called)

    @patch.object(django.contrib.messages, 'error')
    def test_verify__inactive_account(self, mock_error):
        self.addr.user.is_active = False
        self.addr.user.save()
        response = Verify.as_view()(self.request, self.addr.pk,
            self.addr.verif_key)
        self.assertTrue(mock_error.called)

    @patch.object(django.contrib.messages, 'error')
    def test_verify__already_verified(self, mock_error):
        self.addr.verified_at = now()
        self.addr.save()
        response = Verify.as_view()(self.request, self.addr.pk,
            self.addr.verif_key)
        self.assertTrue(mock_error.called)

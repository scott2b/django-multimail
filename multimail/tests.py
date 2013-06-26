from multimail.models import EmailAddress
from multimail.views import Verify
from multimail.settings import MM
from mock import Mock, patch
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.test.client import RequestFactory
import django, multimail, unittest

try:
    from django.utils import timezone
    now = lambda: timezone.now()
except ImportError:
    import datetime
    now = lambda: datetime.datetime.now()


class EmailAddressTest(unittest.TestCase):

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

class VerifyTest(unittest.TestCase):
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

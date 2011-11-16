from django.contrib import messages
from django.contrib.sites.models import Site
from django.dispatch import Signal
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View
from models import EmailAddress
from multimail.settings import MM
from multimail.util import build_context_dict
import datetime

email_verified = Signal(providing_args=[])


class Verify(View):

    def get(self, request, email_pk, verif_key, next=MM.POST_VERIFY_URL):
        try:
            email = EmailAddress.objects.get(pk=email_pk, verif_key=verif_key)
            if email.is_verified():
                raise email.AlreadyVerified()
            if not MM.ALLOW_VERIFICATION_OF_INACTIVE_ACCOUNTS and \
                    not email.user.is_active:
                raise email.InactiveAccount()
            email.remote_addr = request.META.get('REMOTE_ADDR')
            email.remote_host = request.META.get('REMOTE_HOST')
            email.verified_at = datetime.datetime.now()
            email.save()
            email_verified.send_robust(sender=email)
            site = Site.objects.get_current()
            d = build_context_dict(site, email)
            messages.success(request, MM.EMAIL_VERIFIED_MESSAGE % d,
                fail_silently=not MM.USE_MESSAGES)
        except EmailAddress.DoesNotExist:
            messages.error(request, MM.INVALID_VERIFICATION_LINK_MESSAGE,
                fail_silently=not MM.USE_MESSAGES)
        except email.InactiveAccount:
            messages.error(request, MM.INACTIVE_ACCOUNT_MESSAGE,
                fail_silently=not MM.USE_MESSAGES)
        except email.AlreadyVerified:
            """Only allow a single verification to prevent abuses, such as
            re-verifying on a deactivated account."""
            messages.error(request, MM.EMAIL_ALREADY_VERIFIED_MESSAGE,
                fail_silently=not MM.USE_MESSAGES)
        return redirect(next)


class SendLink(View):

    def get(self, request, email_pk, next=None):
        email = get_object_or_404(EmailAddress, pk=email_pk)
        if email.is_verified():
            messages.error(request, MM.EMAIL_ALREADY_VERIFIED_MESSAGE,
                fail_silently=not MM.USE_MESSAGES)
        else:
            email.send_verification(request=request)
        if next:
            return redirect(next)
        else:
            return redirect(request.META['HTTP_REFERER'])

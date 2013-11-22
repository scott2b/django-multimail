from django.contrib import messages
from django.core.urlresolvers import reverse
from django.dispatch import Signal
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View
from models import EmailAddress
from multimail.settings import MM
from multimail.util import build_context_dict, get_site

try:
    from django.utils import timezone
    now = lambda: timezone.now()
except ImportError:
    import datetime
    now = lambda: datetime.datetime.now()

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
            email.verified_at = now()
            email.save()
            email_verified.send_robust(sender=email)
            site = get_site()
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


def set_as_primary(request, email_pk):
    """Set the requested email address as the primary. Can only be
    requested by the owner of the email address."""
    email = get_object_or_404(EmailAddress, pk=email_pk)
    if email.is_verified():
        messages.error(request, 'Email %s needs to be verified first.' % email)
    if email.user != request.user:
        messages.error(request, 'Invalid request.')
    else:
        email.set_primary()
        messages.success(
            request, '%s is now marked as your primary email address.' % email
        )

    try:
        return redirect(request.META['HTTP_REFERER'])
    except KeyError:
        return redirect(reverse(MM.SET_AS_PRIMARY_REDIRECT))


def delete_email(request, email_pk):
    """Delete the given email. Must be owned by current user."""
    email = get_object_or_404(EmailAddress, pk=int(email_pk))
    if email.user == request.user:
        if not email.is_verified():
            email.delete()
        else:
            num_verified_emails = len(request.user.emailaddress_set.filter(
                verified_at__isnull=False))
            if num_verified_emails > 1:
                email.delete()
            elif num_verified_emails == 1:
                if MM.ALLOW_REMOVE_LAST_VERIFIED_EMAIL:
                    email.delete()
                else:
                    messages.error(request,
                        MM.REMOVE_LAST_VERIFIED_EMAIL_ATTEMPT_MSG,
                            extra_tags='alert-error')
    else:
        messages.error(request, 'Invalid request.')
    return redirect(MM.DELETE_EMAIL_REDIRECT)

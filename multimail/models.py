import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.models import Site, get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.db import models
from django.db.models.signals import post_save
from django.template import Context
from django.template.loader import get_template
from django.utils.hashcompat import sha_constructor
from multimail.settings import MM
from multimail.util import build_context_dict
from random import random


class EmailAddress(models.Model):
    """An e-mail address for a Django User. Users may have more than one
    e-mail address. The address that is on the user object itself as the
    email property is considered to be the primary address, for which there
    should also be an EmailAddress object associated with the user."""
    #class Meta:
    #    unique_together = (('user', 'email'),)

    user         = models.ForeignKey(User)
    email        = models.EmailField(max_length=100,null=True,unique=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    verif_key    = models.CharField(max_length=40)
    verified_at  = models.DateTimeField(default=None,null=True,blank=True)
    remote_addr  = models.IPAddressField(null=True,blank=True)
    remote_host  = models.CharField(max_length=255,null=True,blank=True)
    is_primary   = models.BooleanField(default=False)

    def __unicode__(self):
        return self.email

    def is_verified(self):
        """Is this e-mail address verified? Verification is indicated by
        existence of a verified_at timestamp which is the time the user
        followed the e-mail verification link."""
        return bool(self.verified_at)

    def _set_primary_flags(self):
        """Set this email's is_primary to True and all others for this
        user to False."""
        for email in self.user.emailaddress_set.all():
            if email == self:
                if not email.is_primary:
                    email.is_primary = True
                    email.save()
            else:
                if email.is_primary:
                    email.is_primary = False
                    email.save()

    def set_primary(self):
        """Set this e-mail address to the primary address by setting the
        email property on the user."""
        self.user.email = self.email
        self.user.save()
        self._set_primary_flags()

    def save(self, verify=True, request=None, *args, **kwargs):
        """Save this EmailAddress object."""
        if not self.verif_key:
            salt = sha_constructor(str(random())).hexdigest()[:5]
            self.verif_key = sha_constructor(salt + self.email).hexdigest()
        if verify and not self.pk:
            verify = True
        else:
            verify = False
        super(EmailAddress,self).save(*args, **kwargs)
        if verify:
            self.send_verification(request=request)

    def delete(self):
        """Delete this EmailAddress object."""
        primary = self.is_primary
        user = self.user
        super(EmailAddress, self).delete()
        addrs = user.emailaddress_set.all()
        if addrs:
            addrs[0].set_primary()
        else:
            if MM.DELETE_PRIMARY:
                user.email = ''
                user.save()


    def send_verification(self, request=None):
        """Send email verification link for this EmailAddress object.
        Raises smtplib.SMTPException, and NoRouteToHost.
        """
        html_template = get_template(MM.VERIFICATION_EMAIL_HTML_TEMPLATE)
        text_template = get_template(MM.VERIFICATION_EMAIL_TEXT_TEMPLATE)
        if request:
            site = get_current_site(request)
        else:
            try:
                site = Site.objects.get_current()
            except (ImproperlyConfigured, Site.DoesNotExist):
                # This is not a real Site object in the database, just
                # something to use as a placeholder.
                site = Site(domain='www.example.com', name='Example', pk=0)
        d = build_context_dict(site, self)
        context = Context(d)
        msg = EmailMultiAlternatives(MM.VERIFICATION_EMAIL_SUBJECT % d,
            text_template.render(context),MM.FROM_EMAIL_ADDRESS,
            [self.email])
        msg.attach_alternative(html_template.render(context), 'text/html')
        msg.send(fail_silently=False)
        message = MM.VERIFICATION_LINK_SENT_MESSAGE % d
        if request is not None:
            messages.success(request, message,
                fail_silently=not MM.USE_MESSAGES)
        else:
            self.user.message_set.create(message=message)

    class InactiveAccount(Exception):
        """Raised when an account is required to be active.

        .. todo:: is InactiveAccount being used?
        """
        pass

    class AlreadyVerified(Exception):
        """Raised when a verfication request is made for an e-mail address
        that is already verified."""
        pass

### HANDLERS ###

def email_address_handler(sender, **kwargs):
    """Ensures that there is a multimail version of the email address on the
    django user object and that email is set to primary."""
    user = kwargs['instance']
    if not user.email:
        return
    if kwargs.get('raw', False): # don't create email entry when loading fixtures etc.
        return
    try:
        if MM.SEND_EMAIL_ON_USER_SAVE_SIGNAL:
            a,created = EmailAddress.objects.get_or_create(user=user,email=user.email)        
        else:
            try:
                a = EmailAddress.objects.get(user=user,email=user.email)
                # Provides that an address that has been just verified without use of django-multimail,
                # is still considered verified in conditions of django-multimail
                if user.is_active and not a.verified_at:
                    a.verified_at = datetime.datetime.now()
                    a.save(verify=False)
            except EmailAddress.DoesNotExist:
                a = EmailAddress()
                a.user = user
                a.email = user.email
            a.save( verify=False )            
        a._set_primary_flags() # do this for every save in case things get out of sync
    except Exception:
        msg = """An attempt to create EmailAddress object for user %s, email
%s has failed. This may indicate that an EmailAddress object for that email
already exists in the database. This situation can occur if, for example, a
user is manually created through the admin panel or the shell with an email
address that is the same as an existing EmailAddress objects.""" % (
user.username, user.email)
        mail_admins("Failed attempt to create Multimail email address.", msg)
post_save.connect(email_address_handler, sender=User)

def user_deactivation_handler(sender, **kwargs):
    if not MM.USER_DEACTIVATION_HANDLER_ON:
        return
    """Ensures that an administratively deactivated user does not have any
    lingering unverified email addresses."""
    created = kwargs['created']
    user = kwargs['instance']
    if not created and not user.is_active:
        for email in user.emailaddress_set.all():
            if not email.is_verified():
                email.delete()
post_save.connect(user_deactivation_handler, sender=User)

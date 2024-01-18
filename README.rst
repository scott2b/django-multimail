Django Multimail is no longer actively maintained

Django Multimail Requires Django 1.4+
=====================================

multimail is a simple Django application that provides multiple-email address
functionality for Django's existing User model. Features include:

 * Auto-creation of a multimail email from the email on a User object

 * Email verification via link sent to new email address

 * Auto-deletion of unverified email addresses when a user is administratively
   deactivated.

DJANGO COMPATIBILITY NOTE
=========================

django-multimail is tested against Django versions 1.4, 1.5, 1.6, and 1.7.
Please report any known issues with any of these Django versions.

CHANGELOG
=========

0.1.3
-----

Breaks Django 1.3 Compatability. django-multimail is now compatible with
Django 1.4+.

TESTING
=======

To run the test suite:

    $ demo/manage.py test

QUICKSTART 
==========

If you already have email sending configured and Sites configured. (See
detailed setup for alternatives to configuring Sites)
 
 * pip install django-multimail
 * add multimail to installed apps
 * include 'django.template.loaders.eggs.Loader' in your TEMPLATE_LOADERS
 * In your base urls.py:
    (r'^mail/', include('multimail.urls')),
 * syncdb

DETAILED START
==============

 * Configure your project for sending email. This usually involves setting
   the following properties in your settings file: EMAIL_HOST, EMAIL_HOST_USER,
   EMAIL_HOST_PASSWORD, EMAIL_USE_TLS, EMAIL_BACKEND.  (See the Django docs:
   https://docs.djangoproject.com/en/1.7/topics/email/).  Additionally, you
   will need to set either MULTIMAIL_FROM_EMAIL_ADDRESS or ADMIN_EMAIL for
   Multimail to use as the from mail address. ADMIN_EMAIL is used if
   MULTIMAIL_FROM_EMAIL_ADDRESS has not been set.

 * Be sure you are setup to use Django's sites framework (see the Django
   docs: https://docs.djangoproject.com/en/1.7/ref/contrib/sites/).

   multimail uses the current domain to build verification link URLs.
   Alternatively, you can set the MULTIMAIL_EMAIL_VERIFICATION_URL settings
   property. See the SETTINGS section below. Another option is to set both
   the MULTIMAIL_SITE_DOMAIN, and MULTIMAIL_SITE_NAME. When both of these
   are set, they will override the configured site settings (for multimail
   purposes only).

 * Use of the messages framework is now optional. To use messages, set
   MULTIMAL_USE_MESSAGES to True. Be sure you are exposing messages in your
   templates. See Django docs on the messages framework:
   https://docs.djangoproject.com/en/1.7/ref/contrib/messages/

 * Be sure to include 'django.template.loaders.eggs.Loader' in the
   TEMPLATE_LOADERS in your settings file. You should put this after loaders
   that load templates you create yourself so that you can create overriding
   templates to replace the builtin multimail templates.

 * To install: pip install django-multimail

   Or, to install from source:

   pip install git+git@github.com:scott2b/django-multimail.git#egg=multimail

   or, download the code and run python setup.py install

 * Add multimail to your installed apps in your settings file

 * In your base url config, add a line like the following:
    (r'^mail/', include('multimail.urls')),

   The path name 'mail' is arbitrary and can be set to whatever you choose.

 * Run syncdb

You can now start creating new EmailAddress objects for your users. A
Verification email will be sent automatically when a new EmailAddress object is
created.

EXAMPLE
=======

>>> from django.contrib.auth.models import User
>>> u = User.objects.all()[0]
>>> u.save() # will automatically create an EmailAddress object for the user's current email address

You can also create EmailAddress objects for users directly:
>>> from multimail.models import EmailAddress
>>> addr = EmailAddress.objects.create(email='user@example.com', user=u)

SETTINGS
========

The following properties may be set to customize your multimail installation.
Note that where default properties are enclosed with _() indicates translation
via Django's ugettext. Multimail does not currently have any built-in
translations for its default messages. See the Django docs for information
about creating translation messages: https://docs.djangoproject.com/en/1.7/topics/i18n/translation/#how-to-create-language-files

MULTIMAIL_ALLOW_VERIFICATION_OF_INACTIVE_ACCOUNTS
    Default: False. Whether to allow users to verify emails associated
    with a deactivated account.

MULTIMAIL_AUTOVERIFY_ACTIVE_ACCOUNTS
    Default: True. Whether to verify accounts that have been set as active
    outside of django-multimail.

MULTIMAIL_DELETE_PRIMARY
    Default: False. Whether to clear the email field on the user object
    when the last EmailAddress is deleted.

MULTIMAIL_VERIFICATION_LINK_SENT_MESSAGE
    Default: _("A verification link has been sent to %(email)s")

MULTIMAIL_FROM_EMAIL_ADDRESS
    Default: None, but falls back to ADMIN_EMAIL if not available

MULTIMAIL_EMAIL_ALREADY_VERIFIED_MESSAGE
    Default: _("This email address has already been verified.")

MULTIMAIL_EMAIL_VERIFIED_MESSAGE **(See note below)
    Default: _("Thank you for verifying your email address.")

MULTIMAIL_EMAIL_VERIFICATION_URL **(See note below)
    Default: 'http://%(current_site_domain)s/mail/verify/%(emailaddress_id)s/%(verif_key)s'

    Notes: if you change this URL and/or the URL configuration for calling
           the Verify view, you need to be sure that you are passing the
           emailaddress id, and the verification key into the view call.

           Current site domain is generally acquired from the Sites
           configuration, but can be overridden by setting BOTH the
           MULTIMAIL_SITE_DOMAIN and the MULTIMAIL_SITE_NAME

MULTIMAIL_INACTIVE_ACCOUNT_MESSAGE
    Default: _("The account associated with this email address has been marked as inactive. Please contact the site administrator.")

MULTIMAIL_INVALID_VERIFICATION_LINK_MESSAGE
    Default: _("The seleted email verification link is invalid. Please re-register your email address.")

MULTIMAIL_POST_VERIFY_URL
    Default: '/'

MULTIMAIL_USE_MESSAGES
    Default: False. Set to True to enable messages using Django's
    messages framework.

MULTIMAIL_VERIFICATION_EMAIL_SUBJECT **(See note below)
    Default:  _('Verfication required')

MULTIMAIL_VERIFICATION_EMAIL_HTML_TEMPLATE
    Default: 'multimail/verification_email.html'

MULTIMAIL_VERIFICATION_EMAIL_TEXT_TEMPLATE
    Default: 'multimail/verification_email.txt'

**NOTE: properties marked with ** receive a context dictionary for string
templating. The default values do not take advantage of this, preferring
static strings in order to take advantage of translation capabilities. The
following keys are passed to these strings:
current_site_domain
        current_site_id
        current_site_name
        emailaddress_id
        email (the email on the current multimail email object)
        first_name
        last_name
        primary_email (the email on the user object)
        user_id
        username
        verif_key
        verify_link

Note that MULTIMAIL_EMAIL_VERIFICATION_URL does not get the verif_link key
for security reasons.

MULTIMAIL_FROM_EMAIL_ADDRESS
    Defaults to using the ADMIN_EMAIL

MULTIMAIL_SEND_EMAIL_ON_USER_SAVE_SIGNAL
    Default: True. Affects the behavior of notifications when an email address
    is created as a result of a user save. Multimail ensures that there is
    a multimail version of the email on the user object (which is considered
    to be the primary email address for the user). If a user save results
    in the creation of a new EmailAddress object, the default behavior is to
    send a verification link for that new address. Set this to False to
    turn off that behavior.

MULTIMAIL_USER_DEACTIVATION_HANDLER_ON
    Default: False. The old default was to cleanup any lingering, unverified
    email addresses on user save. This can be a nuisance if your user objects
    are getting modified and saved before users have the opportunity to
    verify their email address. If you know for sure that you do not need
    to save users between the time it takes to send a verification link
    and the user clicking the link, then it is probably safe to set this to
    True for automated cleanup of lingering unverified emails. Otherwise, it
    is probably best to delete unverified emails manually.

    I am open to suggestions as to how to better handle automated cleanup of
    lingering unverified email addresses.

MULTIMAIL_EMAIL_ADMINS
    Default: True. Multimail may send notification emails to the site admin
    for some errors that occur. Set this to False to disable those emails.

MULTIMAIL_SITE_DOMAIN
    Default: None. Set to override the site domain for use in multimail
    templates and template strings. Requires both this and MULTIMAIL_SITE_NAME
    to be set to non-None values.

MULTIMAIL_SITE_NAME
    Default: None. Set to override the site name for use in multimail
    templates and template strings. Requires both this and
    MULTIMAIL_SITE_DOMAIN to be set to non-None values.

MULTIMAIL_SET_AS_PRIMARY_REDIRECT
    Default: 'profile'. Reverse name to redirect to after a call to the
    built-in set-as-primary view. Defaults to 'profile'. Currently does not
    handle passing of parameters -- if your user profiles require parameters
    (such as the username or user pk) then you will need to implement your own
    view for handling a set-as-primary request. For details, see
    multimail.views.set_as_primary in the source code.

MULTIMAIL_ALLOW_REMOVE_LAST_VERIFIED_EMAIL
    Default: False. Whether to allow the user to delete all verified
    emails.

MULTIMAIL_REMOVE_LAST_VERIFIED_EMAIL_ATTEMPT_MSG
    Default: "Cannot remove last verified email. Add another verified email
    address to remove the existing one." Message sent when user tries
    to delete the last verified email. Only if
    MULTIMAIL_ALLOW_REMOVE_LAST_VERIFIED_EMAIL is False.

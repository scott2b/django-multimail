from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class Settings(dict):
    def __getattr__(self, index):
        return getattr(settings, 'MULTIMAIL_%s'%index,
            getattr(settings, 'MULTIMAIL_SETTINGS', {}).get(index,
            super(Settings, self).get(index)))

MM = Settings(
    ALLOW_VERIFICATION_OF_INACTIVE_ACCOUNTS = False,
    AUTOVERIFY_ACTIVE_ACCOUNTS = True,
    DELETE_PRIMARY = False,
    VERIFICATION_LINK_SENT_MESSAGE = \
        _("A verification link has been sent to %(email)s"),
    EMAIL_ALREADY_VERIFIED_MESSAGE = \
        _("This e-mail address has already been verified."),
    EMAIL_VERIFIED_MESSAGE = _("Thank you for verifying your e-mail address."),
    EMAIL_VERIFICATION_URL = 'http://%(current_site_domain)s/mail/verify/%(emailaddress_id)s/%(verif_key)s',
    INACTIVE_ACCOUNT_MESSAGE = _("The account associated with this e-mail address has been deactivated. Please contact the site administrator."),
    INVALID_VERIFICATION_LINK_MESSAGE = _("The seleted e-mail verification link is invalid. Please re-register your e-mail address."),
    POST_VERIFY_URL = '/',
    USE_MESSAGES = False,
    VERIFICATION_EMAIL_SUBJECT = _('Verfication required'),
    VERIFICATION_EMAIL_HTML_TEMPLATE = 'multimail/verification_email.html',
    VERIFICATION_EMAIL_TEXT_TEMPLATE = 'multimail/verification_email.txt',
    FROM_EMAIL_ADDRESS = getattr(settings, 'ADMIN_EMAIL', ''),
    SEND_EMAIL_ON_USER_SAVE_SIGNAL = True,
    USER_DEACTIVATION_HANDLER_ON = False,
    EMAIL_ADMINS = True,
    SITE_DOMAIN = None,
    SITE_NAME = None,
    SET_AS_PRIMARY_REDIRECT = 'profile',
    ALLOW_REMOVE_LAST_VERIFIED_EMAIL = False,
    REMOVE_LAST_VERIFIED_EMAIL_ATTEMPT_MSG = "Cannot remove last verified email. Add another verified email address to remove the existing one.",
    DELETE_EMAIL_REDIRECT = 'profile'
)

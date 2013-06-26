from multimail.settings import MM
from django.contrib.sites.models import Site, get_current_site
from django.core.exceptions import ImproperlyConfigured

def build_context_dict(site, emailobj):
    user = emailobj.user
    d = {
        'current_site_domain': site.domain,
        'current_site_id': site.pk,
        'current_site_name': site.name,
        'emailaddress_id': emailobj.pk,
        'email': emailobj.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'primary_email': user.email,
        'user_id': user.pk,
        'username': user.username,
        'verif_key': emailobj.verif_key,
    }
    verify_link = MM.EMAIL_VERIFICATION_URL % d
    d['verify_link'] = verify_link
    return d


def get_site(request=None):
    """Return Site object according to Multimail configuration preferences.
    SITE_DOMAIN / SITE_NAME if they are both set in the Multimail settings.
    Otherwise, try the current sites configuration (using the request object
    if it is available) and finally fall back to example.com / Example rather
    than throwing an exception for wrong configurations."""
    if getattr(MM, 'SITE_DOMAIN') is not None and \
            getattr(MM, 'SITE_NAME') is not None:
        site = Site(domain=MM.SITE_DOMAIN, name=MM.SITE_NAME, pk=0)
    else:
        if request is not None:
            site = get_current_site(request)
        else:
            try:
                site = Site.objects.get_current()
            except (ImproperlyConfigured, Site.DoesNotExist):
                domain = 'example.com'
                name = 'Example'
                site = Site(domain=domain, name=name, pk=0)
    return site

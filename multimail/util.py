from multimail.settings import MM

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

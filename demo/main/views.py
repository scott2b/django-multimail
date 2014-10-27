from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic.base import View
from django.views.generic import TemplateView
from forms import EditUserForm, AddEmailForm
from multimail.models import EmailAddress


def _login(request, user):
    login(request, user)
    messages.info(request, "You are logged in as user %s" % user.username)


class Main(View):

    def get(self, request):
        new_user_form = UserCreationForm()
        auth_form = AuthenticationForm(initial={'next':reverse('main')})
        page_title = 'Home'
        return render_to_response('main.html', locals(),
            context_instance=RequestContext(request))

    def post(self, request):
        if request.POST['form-name'] == 'auth-form':
            new_user_form = UserCreationForm()
            auth_form = AuthenticationForm(data=request.POST)
            if auth_form.is_valid():
                _login(request, auth_form.get_user())
                return redirect('/profile/')
        elif request.POST['form-name'] == 'new-user-form':
            auth_form = AuthenticationForm()
            new_user_form = UserCreationForm(request.POST)
            if new_user_form.is_valid():
                user = new_user_form.save()
                user = authenticate(username=user.username,
                    password=new_user_form.cleaned_data['password1'])
                _login(request, user)
                return redirect('/profile/')
        page_title = 'Home'
        return render_to_response('main.html', locals(),
            context_instance=RequestContext(request))
            
class Profile(View):

    def get(self, request):
        edit_user_form = EditUserForm(instance=request.user)
        add_email_form = AddEmailForm(instance=EmailAddress(
            user=request.user))
        page_title = 'Profile'
        return render_to_response('profile.html', locals(),
            context_instance=RequestContext(request))

    def post(self, request):
        if request.POST['form-name'] == 'edit-user-form':
            add_email_form = AddEmailForm()
            edit_user_form = EditUserForm(request.POST, instance=request.user)
            if edit_user_form.is_valid():
                edit_user_form.save()
                return redirect('/profile/')
        if request.POST['form-name'] == 'add-email-form':
            edit_user_form = EditUserForm(instance=request.user)
            add_email_form = AddEmailForm(request.POST)
            if add_email_form.is_valid():
                add_email_form.save()
                return redirect('/profile/')
        page_title = 'Profile'
        return render_to_response('profile.html', locals(),
            context_instance=RequestContext(request))


class DeleteUser(View):

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        if user == request.user:
            user.delete()
        messages.info(request, "The user account for %s has been deleted" % username)
        return redirect('/')

DELETE_MESSAGE = """
<h3>Deleted e-mail address: %s</h3>
<p>When deleting an EmailAddress object, multimail will change the user's
primary email if necessary to a remaining available address. If the last
EmailAddress has been deleted, multimail will clear the user's email field
if the MULTIMAIL_DELETE_PRIMARY settings property is set to True. The default
value for this setting is False, but is set to True for this demo.</p>
"""
class DeleteEmail(View):

    def get(self, request, email_id):
        if not request.user.is_authenticated():
            messages.error(request,
                "<p>You must login to delete your e-mail addresses.</p>")
            return redirect('main')
        email = get_object_or_404(EmailAddress, pk=email_id)
        if request.user == email.user:
            msg = DELETE_MESSAGE % email.email
            email.delete()
            messages.info(request, msg)
        else:
            messages.error(request,
                "<p>You have tried to delete another user's email address.</p>")
        return redirect('/profile/')

SET_PRIMARY_MESSAGE = """
<h3>Your primary e-mail address has been set to: %s</h3>
<p>Multimail uses the email field on the User object as the primary e-mail
address. You can set the field directly or call the set_primary method
on a multimail EmailAddress object.</p>
"""
class SetPrimaryEmail(View):

    def get(self, request, email_id):
        if not request.user.is_authenticated():
            messages.error(request,
                "<p>You must login to set your primary e-mail address.</p>")
            return redirect("main")
        email = get_object_or_404(EmailAddress, pk=email_id)
        if request.user == email.user:
            email.set_primary()
            messages.info(request, SET_PRIMARY_MESSAGE % email.email)
        else:
            messages.error(request,
                "<p>Invalid request to set primary e-mail address.</p>")
        return redirect('/profile/')

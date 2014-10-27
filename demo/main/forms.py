from django.contrib.auth.models import User
from django import forms
from multimail.models import EmailAddress

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class AddEmailForm(forms.ModelForm):

    class Meta:
        model = EmailAddress
        fields = ('email', 'user')
    user = forms.ModelChoiceField(queryset=User.objects.all(),
        widget=forms.HiddenInput)

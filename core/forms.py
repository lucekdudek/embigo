# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    """
    Form for registering a new user account, with email required.
    Validates that the requested username and email is not already in use, and
    requires the password to be entered twice to catch typos.
    """
    email = forms.EmailField(
        widget = forms.TextInput(),
        required=True
    )

    class Meta(UserCreationForm.Meta):
        fields = [
            User.USERNAME_FIELD,
            'email',
            'password1',
            'password2'
        ]
        required_css_class = 'required'

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the site.
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError("Ten adres email jest już zarejestrowany."
                                        "Proszę wprowadź inny adres email.")
        return self.cleaned_data['email']

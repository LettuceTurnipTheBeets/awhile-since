from django.contrib.auth.models import User
from django import forms
from .models import UserProfile
from reminder.choices import *
from crispy_forms.helper import FormHelper
from captcha.fields import CaptchaField


class UserForm(forms.ModelForm):
    """Form for the basic django User model"""
    password = forms.CharField(widget=forms.PasswordInput())
    retype_password = forms.CharField(widget=forms.PasswordInput())
    captcha = CaptchaField()
    email = forms.CharField(label='Email address', required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False  # don't render form DOM element
        helper.render_unmentioned_fields = True  # render all fields
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-10'
        return helper


class PasswordForm(forms.Form):
    """Form for username and password login"""
    username = forms.CharField(label='Username', required=True)
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        required=True
    )

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False  # don't render form DOM element
        helper.render_unmentioned_fields = True  # render all fields
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-10'
        return helper


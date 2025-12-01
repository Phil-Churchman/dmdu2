from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.forms import ValidationError
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from .validator import *
from .utilities import *
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import NON_FIELD_ERRORS

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from itertools import chain
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3
import pandas as pd
import os
from django.conf import settings

class PrettyJSONWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        # If value is provided and it is not None, format it as pretty JSON
        if value:
            # Ensure it's a valid JSON object, if not, we'll treat it as an empty dict
            try:
                formatted_value = json.dumps(value, indent=4)
            except (TypeError, ValueError):
                formatted_value = json.dumps({})
        else:
            formatted_value = ""
        
        # Call the parent class's render method, but pass the pretty-formatted JSON as value
        return super().render(name, formatted_value, attrs, renderer)

class RegisterForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists!")
        return email 

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields["email"].required = True

class VersionForm(forms.ModelForm):

    class Meta: 
        model = Version 
        fields = '__all__'
        widgets = {'user': forms.HiddenInput(),
                   'archive': forms.HiddenInput(),
                'notes': forms.Textarea(attrs={
                'class': 'form-control',  # Bootstrap class for styling
                'rows': 5,                # Optional: adjust the number of rows
                'placeholder': 'Enter your text here'  # Optional placeholder
            }),}  
            
    def __init__(self, *args, user, new, version, blank, **kwargs):
        super(VersionForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(id=user.id)
        if new:
            lookup = json.loads(Master.objects.get(ref="default").lookup)
            variables = []
            for i in list(lookup["Value"].keys()):
                if blank:
                    variables.append({
                        'name': lookup["Value"][i],
                        'variable': 'NONE',
                        'value': 50,
                        'index': i
                        })
                else:
                    variables.append({
                        'name': lookup["Value"][i],
                        'variable': lookup["Variable"][i],
                        'value': 50,
                        'index': i
                        })
        else:
            variables = get_variables(version)         
        for i in variables:
            self.fields[i["name"]].widget = forms.HiddenInput()
            # if i["variable"] == "NONE":
            #     self.fields[i["name"]].widget = forms.HiddenInput()
            # else:
            #     self.fields[i["name"]].label = i["variable"]

class MethodForm(forms.ModelForm):
    class Meta:
        model = Method 
        fields = '__all__'

    def __init__(self, *args, version, **kwargs):
        self.version = version
        super(MethodForm, self).__init__(*args, **kwargs)
        variables = get_variables(version)
        for i in variables:
            if i["variable"] == "NONE":
                self.fields[i["name"]].widget = forms.HiddenInput()
            else:
                self.fields[i["name"]].label = i["variable"]
        for i in ["index", "version"]:
            self.fields[i].widget = forms.HiddenInput()

        for i in ["long_description"]:
            self.fields[i].widget = forms.Textarea(attrs={
                'rows': 8,      # Number of visible rows
                'placeholder': 'Enter text here...'
                })
        for i in ["links"]:
            self.fields[i].widget = forms.Textarea(attrs={
                'rows': 4,      # Number of visible rows
                'placeholder': 'Enter text here...'
                })
class LookupForm(forms.ModelForm):
    class Meta:
        model = Lookup
        fields = '__all__'           

    def __init__(self, *args, user, **kwargs):
        super(LookupForm, self).__init__(*args, **kwargs)
        ref = {}
        for i in range(10):
            ref["value_" + str(i + 1)] = "Variable " + str(i + 1)
            ref["value_" + str(i + 1) + "_is_option_reqt"] = "Variable " + str(i + 1) + " is a method req't(*)"

        for i in ref.keys():
            self.fields[i].label = ref[i]
        for i in ["version"]:
            self.fields[i].widget = forms.HiddenInput()
        if not user.is_superuser:
            for i in range(10):
                self.fields["value_" + str(i+1) + "_is_option_reqt"].widget = forms.HiddenInput()
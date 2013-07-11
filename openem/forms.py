# coding=utf8

from django import forms

class FormBase(forms.Form):
    def add_field_error(self, field, error):
        errors = self._errors.setdefault(field, forms.util.ErrorList())
        errors.append(error)

    def add_error(self, error):
        self.add_field_error(forms.forms.NON_FIELD_ERRORS, error)

class LoginForm(FormBase):
    name = forms.CharField(
        label=u'שם בדוי', 
        max_length=30,
        error_messages= {'required':u'איך אפשר בלי שם?'}
    )
    password = forms.CharField(
        label=u'סיסמא', 
        max_length=30,
        widget=forms.PasswordInput(),
        error_messages= {'required':u'איך אפשר בלי סיסמא?'}
    )

    def clean_name(self):
        return self.cleaned_data['name'].strip()

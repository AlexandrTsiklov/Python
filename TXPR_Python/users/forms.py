from django import forms
from django.core.exceptions import ValidationError
from users.models import *



#--------------------Формы регистрации и авторизации--------------------

class RegistrationForm(forms.ModelForm):

    password1 = forms.CharField(label='password_1')
    password2 = forms.CharField(label='password_2')

    class Meta:
        model = MyUser
        # fields = ('person_id', 'username', 'fio', 'gender', 'date_of_birth', 'email', 'number')
        fields = ('username',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают!!!")
        return password2

    def save(self, commit=True):
        our_user = super().save(commit=False)
        our_user.set_password("password2")
        if commit:
            our_user.save()
        return our_user


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль')


class LoadAvatar(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ('photo',)
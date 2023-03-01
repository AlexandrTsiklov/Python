from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import *
from users.forms import RegistrationForm


class MyUserAdmin(admin.ModelAdmin):
    add_form = RegistrationForm
    # list_display = ('username', 'password', 'fio', 'date_of_birth', 'email', 'number')
    # fields = ('username', 'password', 'fio', 'gender', 'date_of_birth', 'email', 'number')
    list_display = ('username', 'password')
    fields = ('username', 'password')

    def save_model(self, request, our_user, form, change):
        our_user.set_password(our_user.password)
        print(type(our_user))
        our_user.save()


admin.site.register(MyUser, MyUserAdmin) # порядок важен
admin.site.register(Orders)
admin.site.unregister(Group)
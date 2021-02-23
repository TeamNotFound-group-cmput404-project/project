

"""
https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html


"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email  = forms.EmailField()
    class Meta:
        model = User
        # not implement url yet
        fields = ['username','email','password1', 'password2',]
       
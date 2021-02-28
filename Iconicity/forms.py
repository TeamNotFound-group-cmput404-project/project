

"""
https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html

https://www.youtube.com/watch?v=CQ90L5jfldw&list=RDCMUCCezIgC97PvUuR4_gbFUs5g&index=9
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import fields
from .models import UserProfile, Post

class SignUpForm(UserCreationForm):
    github = forms.URLField(max_length=254, help_text='Optional.')
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'username', 'github', )
       
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'github', 'host', 'follow']

class PostsCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'visibility']

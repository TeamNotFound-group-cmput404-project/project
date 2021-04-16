from django.test import TestCase,Client
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Iconicity.views import *
from django.contrib.auth.models import User
from Iconicity.forms import SignUpForm,ProfileUpdateForm,PostsCreateForm,UserUpdateForm
from Iconicity.models import Post,FriendRequest,UserProfile


class TestForms(TestCase):
	def test_sign_up_form(self):
		form =  SignUpForm(data = {
			'email':'test@gmail.com',
			'password1':'123linyu',
			'password2':'123linyu',
			'username':'test',
			'github':'https://github.com/Meilin-Lyu'
			}
		)
		self.assertTrue(form.is_valid())

	def test_profile_update_form(self):
		form = ProfileUpdateForm (data = {
			'github':'https://github.com/update'
			}
		)
		self.assertTrue(form.is_valid())

	def test_posts_create_form(self):
		# Should return False
		form = PostsCreateForm(data = {
			'title':'title1',
			'content':'content1',
			'image':'images/image_address.png',
			'visibility':'public'
			}
		)
		self.assertFalse(form.is_valid())

	def test_user_update_form(self):
		form = UserUpdateForm(data = {
			'username':'test',
			'github':'https://github.com/Meilin-Lyu'
			}
		)
		self.assertTrue(form.is_valid())

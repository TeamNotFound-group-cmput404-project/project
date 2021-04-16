from django.test import TestCase,Client
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Iconicity.views import *
from django.contrib.auth.models import User
from Iconicity.forms import SignUpForm,ProfileUpdateForm,PostsCreateForm,UserUpdateForm
from Iconicity.models import Post,FriendRequest,UserProfile


class LoginAndSignUpTest(TestCase):
	def setUp(self):
		self.signup_url = reverse('signup')
		self.login_url = reverse('login')
		self.user = {
			'email':'test@gmail.com',
			'password':'123linyu',
		    'username':'test',
		}
		User.objects.create_user(**self.user)

	def signup_success(self):
		response = self.post(self.login_url,self.user)
		self.assertEquals(response.status_code,200)

	def test_login(self):
		response = self.client.post(self.login_url,self.user)
		self.assertEquals(response.status_code,302)
    
	
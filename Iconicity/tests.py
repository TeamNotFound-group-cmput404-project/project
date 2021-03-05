from django.test import TestCase
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Iconicity.views import LoginView,new_post,logout_view, signup
from Iconicity.views import main_page, AddPostView
from django.contrib.auth.models import User

# Create your tests here.
class TestUrls(SimpleTestCase):
	def test_if_login_resolved(self):
		url = reverse('login')
		self.assertEquals(resolve(url).func.view_class, LoginView)

	def test_if_logout_resolved(self):
		url = reverse('logout')
		self.assertEquals(resolve(url).func, logout_view)

	def test_if_signup_resolved(self):
		url = reverse('signup')
		self.assertEquals(resolve(url).func, signup)

	def test_if_main_page_resolved(self):
		url = reverse('main_page')
		self.assertEquals(resolve(url).func, main_page)

	def test_if_new_post_resolved(self):
		url = reverse('new_post')
		self.assertEquals(resolve(url).func, new_post)

	def test_if_login_resolved(self):
		url = reverse('post_form')
		self.assertEquals(resolve(url).func.view_class, AddPostView)

class LoginTest(TestCase):
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

	def test_view(self):
		response = self.client.get(self.signup_url)	
		self.assertEquals(response.status_code,200)

	

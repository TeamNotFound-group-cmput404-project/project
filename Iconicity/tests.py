from django.test import TestCase
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Iconicity.views import LoginView, logout_view, signup
from Iconicity.views import main_page, make_post, new_post, AddPostView
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

	def test_if_make_post_resolved(self):
		url = reverse('make_post')
		self.assertEquals(resolve(url).func, make_post)

	def test_if_new_post_resolved(self):
		url = reverse('new_post')
		self.assertEquals(resolve(url).func, new_post)

	def test_if_login_resolved(self):
		url = reverse('post_form')
		self.assertEquals(resolve(url).func.view_class, AddPostView)
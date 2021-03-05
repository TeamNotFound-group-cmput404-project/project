from django.test import TestCase,Client
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Iconicity.views import LoginView,logout_view, signup
from Iconicity.views import main_page, AddPostView
from django.contrib.auth.models import User
from Iconicity.forms import SignUpForm,ProfileUpdateForm,PostsCreateForm,UserUpdateForm
from Iconicity.models import Post,FriendRequest,UserProfile

# Create your tests here.
class TestUrls(SimpleTestCase):
	def test_if_login_resolved(self):
		url = reverse('login')
		print("1")
		self.assertEquals(resolve(url).func.view_class, LoginView)

	def test_if_logout_resolved(self):
		url = reverse('logout')
		print("2")
		self.assertEquals(resolve(url).func, logout_view)

	def test_if_signup_resolved(self):
		url = reverse('signup')
		print("3")
		self.assertEquals(resolve(url).func, signup)

	def test_if_main_page_resolved(self):
		url = reverse('main_page')
		print("4")
		self.assertEquals(resolve(url).func, main_page)

	def test_if_login_resolved(self):
		url = reverse('post_form')
		print("5")
		self.assertEquals(resolve(url).func.view_class, AddPostView)

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
		print("6")
		response = self.post(self.login_url,self.user)
		self.assertEquals(response.status_code,200)

	def test_login(self):
		print("7")
		response = self.client.post(self.login_url,self.user)
		self.assertEquals(response.status_code,302)

	def test_view(self):
		print("8")
		response = self.client.get(self.signup_url)	
		self.assertEquals(response.status_code,200)


	
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
		print("9",form.is_valid)
		self.assertTrue(form.is_valid())

	def test_posts_create_form(self):
		# Should return False
		form = PostsCreateForm(data = {
			'title':'title1',
			'content':'content1',
			'visibility':'public',
			}
		)
		self.assertTrue(form.is_valid())

	def test_user_update_form(self):
		form = UserUpdateForm(data = {
			
			'username':'test',
			'github':'https://github.com/Meilin-Lyu'
			}
		)
		self.assertTrue(form.is_valid())



	
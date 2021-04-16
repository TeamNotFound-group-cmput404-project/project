from django.test import TestCase,Client
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Iconicity.views import *
from django.contrib.auth.models import User
from Iconicity.forms import SignUpForm,ProfileUpdateForm,PostsCreateForm,UserUpdateForm
from Iconicity.models import Post,FriendRequest,UserProfile

class TestUrls(SimpleTestCase):

	def test_logout(self):
		url = reverse('logout')
		self.assertEquals(resolve(url).func, logout_view)

	def test_main_page(self):
		url = reverse('public')
		self.assertEquals(resolve(url).func, mainPagePublic)
	
	def test_profile(self):
		url = reverse('profile')
		self.assertEquals(resolve(url).func, profile)

	def test_repost(self):
		url = reverse('repost')
		self.assertEquals(resolve(url).func, repost)

	def test_mypost(self):
		url = reverse('mypost')
		self.assertEquals(resolve(url).func, mypost)

	def test_public(self):
		url = reverse('public')
		self.assertEquals(resolve(url).func, mainPagePublic)

	def test_friends(self):
		url = reverse('friends')
		self.assertEquals(resolve(url).func, friends)

	def test_following(self):
		url = reverse('follow')
		self.assertEquals(resolve(url).func, following)

	def test_post_form(self):
		url = reverse('post_form')
		self.assertEquals(resolve(url).func.view_class, AddPostView)

	def test_update_post(self):
		url = reverse('update_post')
		self.assertEquals(resolve(url).func, update_post_view)

	def test_delete(self):
		url = reverse('delete')
		self.assertEquals(resolve(url).func, delete_post)

	def test_comment_form(self):
		url = reverse('comment_form')
		self.assertEquals(resolve(url).func, post_comments)

	
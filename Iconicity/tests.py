from django.test import TestCase,Client
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Iconicity.views import *
from django.contrib.auth.models import User
from Iconicity.forms import SignUpForm,ProfileUpdateForm,PostsCreateForm,UserUpdateForm
from Iconicity.models import Post,FriendRequest,UserProfile

# Create your tests here.
class TestUrls(SimpleTestCase):
	def test_login(self):
		url = reverse('login')
		self.assertEquals(resolve(url).func.view_class, LoginView)

	def test_logout(self):
		url = reverse('logout')
		self.assertEquals(resolve(url).func, logout_view)

	def test_signup(self):
		url = reverse('signup')
		self.assertEquals(resolve(url).func, signup)

	def test_main_page(self):
		url = reverse('main_page')
		self.assertEquals(resolve(url).func, main_page)

	def test_repost(self):
		url = reverse('repost')
		self.assertEquals(resolve(url).func, repost)

	def test_profile(self):
		url = reverse('profile')
		self.assertEquals(resolve(url).func, profile)

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
		self.assertEquals(resolve(url).func.view_class, AddCommentView)

	# Friend requests tests:
	def test_follow_someone(self):
		url = reverse('follow_someone')
		self.assertEquals(resolve(url).func, follow_someone)

	def test_unfollow_someone(self):
		url = reverse('unfollow_someone')
		self.assertEquals(resolve(url).func, unfollow_someone)

	def test_friend_requests(self):
		url = reverse('friend_requests')
		self.assertEquals(resolve(url).func, friend_requests_received_view)

	def test_avail_profiles(self):
		url = reverse('avail_profiles')
		self.assertEquals(resolve(url).func, avail_userProfile_list_view)

	def test_all_profiles(self):
		url = reverse('all_profiles')
		self.assertEquals(resolve(url).func.view_class, UserProfileListView)

	def test_send_friendRequest(self):
		url = reverse('send_friendRequest')
		self.assertEquals(resolve(url).func, send_friend_request)

	def test_remove_friend(self):
		url = reverse('remove_friend')
		self.assertEquals(resolve(url).func, remove_friend)

	def test_accept_friend_request(self):
		url = reverse('accept_friend_request')
		self.assertEquals(resolve(url).func, accept_friend_request)

	def test_reject_friend_request(self):
		url = reverse('reject_friend_request')
		self.assertEquals(resolve(url).func, reject_friend_request)

	def test_like_post_friend(self):
		url = reverse('like_post_friend')
		self.assertEquals(resolve(url).func, like_view)

	def test_like_post_mypost(self):
		url = reverse('like_post_mypost')
		self.assertEquals(resolve(url).func, like_view)

	def test_like_post_public(self):
		url = reverse('like_post_public')
		self.assertEquals(resolve(url).func, like_view)

	def test_like_post_following(self):
		url = reverse('like_post_following')
		self.assertEquals(resolve(url).func, like_view)


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
	
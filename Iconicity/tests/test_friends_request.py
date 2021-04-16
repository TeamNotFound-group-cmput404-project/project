from django.test import TestCase,Client
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Iconicity.views import *
from django.contrib.auth.models import User
from Iconicity.forms import SignUpForm,ProfileUpdateForm,PostsCreateForm,UserUpdateForm
from Iconicity.models import Post,FriendRequest,UserProfile

class TestUrls(SimpleTestCase):
    # Friend requests tests:
    def test_follow_someone(self):
        url = reverse('follow_someone')
        self.assertEquals(resolve(url).func, follow_someone)
    
    def test_remove_inbox_follow(self):
        url = reverse('remove_inbox_follow')
        self.assertEquals(resolve(url).func, remove_inbox_follow)
    
    def test_unfollow_someone(self):
        url = reverse('unfollow_someone')
        self.assertEquals(resolve(url).func, unfollow_someone)
    
    def follow_back(self):
        url = reverse('follow_back')
        self.assertEquals(resolve(url).func, follow_back)

    def inbox(self):
        url = reverse('inbox')
        self.assertEquals(resolve(url).func, inbox_view)

    def test_all_profiles(self):
        url = reverse('all_profiles')
        self.assertEquals(resolve(url).func.view_class, UserProfileListView)

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



    

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('', views.LoginView.as_view(), name = 'login'),
	path('logout', views.logout_view, name = 'logout'),
	path('signup',views.signup,name = 'signup'),
	path('main', views.main_page, name = 'main_page'),

	# need to fix this part later
	path('friends/like', views.like_view, name="like_post_friend"),
	path('mypost/like', views.like_view, name="like_post_mypost"),
	path('public/like', views.like_view, name="like_post_public"),
	path('following/like', views.like_view, name="like_post_following"),

	path('repost', views.repost, name='repost'),
	path('profile',views.profile,name = "profile"),
	path('mypost', views.mypost, name = 'my_post'),
	path('public',views.mainPagePublic,name = "main_page"),
	path('friends', views.friends, name = 'friends'),
	path('following',views.following,name = "follow"),
	path('post_form', views.AddPostView.as_view(), name="post_form"),


	# Friend Requests functionalities:
	path('follow_someone', views.follow_someone, name='follow_someone'),
	path('unfollow_someone', views.unfollow_someone, name='unfollow_someone'),
	path('friend_requests', views.friend_requests_received_view, name='friend_requests'),
	path('avail_profiles', views.avail_userProfile_list_view, name='avail_profiles'),
	path('all_profiles', views.UserProfileListView.as_view(), name='all_profiles'),
	path('send_friendRequest', views.send_friend_request, name='send_friendRequest'),
	path('remove_friend', views.remove_friend, name='remove_friend'),
	path('accept_friend_request', views.accept_friend_request, name='accept_friend_request'),
	path('reject_friend_request', views.reject_friend_request, name='reject_friend_request'),

	# APIs
    path(r'posts/', views.Posts().as_view()),
    path(r'posts', views.Posts().as_view()),
	path(r'author/<str:author_id>/posts/<str:post_id>/', views.PostById().as_view()),
    path(r'author/<str:author_id>/posts/<str:post_id>', views.PostById().as_view()),
	path(r'author/<str:author_id>', views.AuthorById().as_view()),
	path(r'author/<str:author_id>/', views.AuthorById().as_view()),
	path(r'author/<str:author_id>/posts/', views.AllPostsByAuthor().as_view()),
	path(r'author/<str:author_id>/posts', views.AllPostsByAuthor().as_view()),
	path(r'author/', views.AllAuthors().as_view()),
	path(r'author', views.AllAuthors().as_view()),
 	#https://iconicity-test-a.herokuapp.com/author/b058b053-4766-4c6a-acaf-561c08badf64/posts/00db788e-45af-49eb-8350-f1c507eb42d0

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

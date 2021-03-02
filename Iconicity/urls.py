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
	path('like', views.like_view, name="like_post"),
	path('profile',views.profile,name = "profile"),
	path('mypost', views.mypost, name = 'my_post'),
	path('public',views.main_page,name = "public"),
	path('friends', views.friends, name = 'friends'),
	path('following',views.following,name = "follow"),
	path('post_form', views.AddPostView.as_view(), name="post_form"),
	# Below are for friend requests functionalities:
	path('friend_requests', views.friendRequests_received_view, name='friend_requests'),
	path('avail_profiles', views.avail_userProfile_list_view, name='avail_profiles'),
	path('all_profiles', views.UserProfileListView.as_view(), name='all_profiles'),
	path('send_friendRequest', views.send_friendRequest, name='send_friendRequest'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url

urlpatterns = [
	path('', views.LoginView.as_view(), name = 'login'),
	path('logout', views.logout_view, name = 'logout'),
	path('signup',views.signup,name = 'signup'),
	path('main', views.main_page, name = 'main_page'),
	path('make_post', views.make_post, name = 'make_post'), # by Shway
	#path('author', views.getUserProfile, name = 'userprofile')
	path('new_post', views.new_post, name = 'new_post'),
	# path('main', views.finish_post, name = 'main_page'),
	path('post_form', views.AddPostView.as_view(), name="post_form")
]
from django.urls import path
from . import views

urlpatterns = [
	path('login', views.login, name = 'login'),
	path('signup',views.signup,name = 'signup'),
	path('main_page', views.main_page, name = 'main_page'),
	path('user_profile', views.user_profile, name = 'user_profile'),
]
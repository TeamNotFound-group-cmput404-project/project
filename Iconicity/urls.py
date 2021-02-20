from django.urls import path
from . import views

urlpatterns = [
	path('', views.login, name = 'login'),
	path('signup',views.signup,name = 'signup'),
	path('main', views.main_page, name = 'main_page'),
]
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .models import Post

# Shway Wang put this here:
# below is put here temperarily, just to display the format

# Create your views here.

def login(request):
	return render(request, 'Iconicity/login.html')

def signup(request):
	form = UserCreationForm()
	return render(request, 'Iconicity/signup.html', {'form': form})

def main_page(request):
	context = {
		'posts': Post.objects.all()
	}
	return render(request, 'Iconicity/main_page.html', context)

def user_profile(request):
	context = {
		'posts': Post.objects.all()
	}
	return render(request, 'Iconicity/user_profile.html', context)
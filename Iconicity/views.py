from django.shortcuts import render
from django.http import HttpResponse
from .models import Post

# Shway Wang put this here:
# below is put here temperarily, just to display the format

# Create your views here.

def login(request):
	return render(request, 'Iconicity/login.html')

def signup(request):
	return render(request, 'Iconicity/signup.html')

def main_page(request):
	context = {
		'posts': Post.objects.all()
	}
	return render(request, 'Iconicity/main_page.html', context)
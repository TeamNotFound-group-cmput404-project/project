from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def login(request):
	return render(request, 'Iconicity/login.html')

def main_page(request):
	return render(request, 'Iconicity/main_page.html')
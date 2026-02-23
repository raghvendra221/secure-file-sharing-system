from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Secure File Sharing System Running")

# Create your views here.

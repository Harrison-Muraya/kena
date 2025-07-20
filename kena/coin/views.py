from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def home(request):
    print('hellow')
    return render(request, 'coin/home.html')

def create(request):
    
    return render(request, 'coin/create.html')
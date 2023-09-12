from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    return render(request, 'main/index.html')


def git(request):
    if request.method == 'POST':
        payload = request.json
        return HttpResponse(payload)

    return HttpResponse('Hello, world. You\'re at the git index.')


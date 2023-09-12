from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    return render(request, 'main/index.html')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def git(request):
    if request.method == 'POST':
        payload = request
        print('anan aa')
        print(payload)
        return HttpResponse(payload)

    return HttpResponse('Hello, world. You\'re at the git index.')


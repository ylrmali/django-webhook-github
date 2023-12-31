from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes
from ipaddress import ip_address, ip_network
from hashlib import sha1
import requests
import hmac
import os
import json

# Create your views here.


def index(request):
    return render(request, 'main/index.html')


@require_POST
@csrf_exempt
def webhook(request):

    data = request.body
    json_data = json.loads(data)
    try:
        branch = json_data['ref'].split('/')[-1]
    except KeyError:
        print('Its just a ping event')
    # Verify if request came from GitHub
    remote_addr = request.META.get('REMOTE_ADDR')
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for and forwarded_for.count(',') >= 1:
        ip = u'{}'.format(forwarded_for.split(',')[0])
    elif len(forwarded_for) == 1:
        ip = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    elif remote_addr and forwarded_for == 'None':
        ip = u'{}'.format(remote_addr)

    client_ip_address = ip_address(ip) # get request ip address
    whitelist = requests.get('https://api.github.com/meta').json()['hooks'] # get github hook's ips

    # control ip address is valid or not
    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return HttpResponseForbidden('Permission denied.')

    # Verify the request signature
    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Permission denied.')

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
    # print((force_bytes(request.body)))
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden('Permission denied.')

    # If request reached this point we are in a good shape
    # Process the GitHub events
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')

    if event == 'ping':
        return HttpResponse('ping')
    elif event == 'push':
        # Control database count and update database
        # if database count is 1, update database and migrate
        databases = settings.DATABASES
        if len(databases) == 1:
            os.system(f'cd {settings.BASE_DIR} \
                    && git pull origin {branch}  \
                    && python3 manage.py makemigrations \
                    && python3 manage.py migrate')

        else:
            for key in databases.keys():
                if key == 'default':
                    continue
                else:
                    os.system(f'cd {settings.BASE_DIR} \
                            && git pull origin {branch}  \
                            && python3 manage.py makemigrations {key} \
                            && python3 manage.py migrate --database={key} \
                            && python3 manage.py migrate')
        # if we user daphne server, we need to restart daphne server
        if 'daphne' in settings.INSTALLED_APPS:
            os.system('sudo supervisorctl restart all')
        return HttpResponse('success')

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)
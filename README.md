# GITHUB WEBHOOK USAGE WITH DJANGO FRAMEWORK

*Github webhook provides a socket for recognize the changes in the repository.*

## **Creating Web Hook**

1. First we have to create web hook  in repository settings.
2. Go to repository → Settings → Webhook →  Add web hook

![webhook.png](GITHUB%20WEBHOOK%204b2b3bc98faa4c39be8fea3526c6928a/webhook.png)

- Here we have 5 input url, content-type, event and active

`Payload URL` → it’s webhook url in our project. We should create a url for webhook.

`Secret` → it’s your secret key to communicate. 

`Content-Type` → it’s response type. Choose **application/json**

`Event Filter` → it’s socket config. You can choose all of them. I use just for push event.

`Active` → it’s webhook status. It should be active for sending request.

1. go to shell and create random string for webhook
    
    ```python
    from django.utils.crypto import get_random_string
    
    In [2]: get_random_string(50)
    Out[2]: u'nuiVypAArY7lFDgMdyC5kwutDGQdDc6rXljuIcI5iBttpPebui'
    # copy this code some where for now
    ```
    
    - go to github webhook settings and paste this code in secret
    - go to [settings.py](http://settings.py) → GITHUB_WEBHOOK_SECRET=’<your_code>’
2. install requirements
    
    ```python
    pip install requests ipaddress
    ```
    
3. go to [setting.py](http://setting.py) and add github secret key
    
    ```python
    GITHUB_WEBHOOK_SECRET=’<your_secret_key>’
    ```
    
4. Now go to your project → [views.py](http://views.py)
    
    ```python
    import hmac
    from hashlib import sha1
    
    from django.conf import settings
    from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
    from django.views.decorators.csrf import csrf_exempt
    from django.views.decorators.http import require_POST
    from django.utils.encoding import force_bytes
    
    import requests
    from ipaddress import ip_address, ip_network
    
    @require_POST
    @csrf_exempt
    def hello(request):
        # Verify if request came from GitHub
        forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
        client_ip_address = ip_address(forwarded_for) # get request ip address
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
        if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
            return HttpResponseForbidden('Permission denied.')
    
        # If request reached this point we are in a good shape
        # Process the GitHub events
        event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')
    
        if event == 'ping':
            return HttpResponse('ping')
        elif event == 'push':
            # go to base director and git pull 
            os.system(f'cd {settings.BASE_DIR} && git pull origin main') 
            return HttpResponse('success')
    
        # In case we receive an event that's not ping or push
        return HttpResponse(status=204)
    ```
    
1. create url for webhook
    
    ```
    urlpatterns = [
    		.
    		.
    		.
        path('webhook/', views.webhook, name='webhook'),
    ]
    ```
    
2. go to your server git pull for last time and enjoy :)

**NOTE:** Don’t forget start your gunicorn with **—reload** flag

```python
gunicorn -b "0.0.0.0:8002" <your_project_name>.wsgi:application --reload
```

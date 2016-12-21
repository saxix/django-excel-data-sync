from django.contrib.auth import authenticate
from django.http import HttpResponse


class BasicAuthMiddleware(object):
    def unauthed(self):
        response = HttpResponse("""<html><title>Auth required</title><body>
                                <h1>Authorization Required</h1></body></html>""")
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        response.status_code = 401
        return response

    def process_request(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            authentication = request.META['HTTP_AUTHORIZATION']
            (authmeth, auth) = authentication.split(' ', 1)
            if 'basic' != authmeth.lower():
                return self.unauthed()
            auth = auth.strip().decode('base64')
            username, password = auth.split(':', 1)
            u = authenticate(username=username, password=password)
            request.user = u
            if not u:
                return self.unauthed()

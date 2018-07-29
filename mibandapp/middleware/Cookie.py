import uuid

class CookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'cart_id' not in request.COOKIES:
            cookie = str(uuid.uuid4())
            response.set_signed_cookie('cart_id', cookie, max_age=365*24*60*60)
        return response

class UserCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if '_t' not in request.COOKIES:
            cookie = str(uuid.uuid4())
            response.set_signed_cookie('_t', cookie, max_age=365*24*60*60)
        return response

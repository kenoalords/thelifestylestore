from mibandapp.models import Cart, Item

def cart_items(request):
    if 'cart_id' in request.COOKIES:
        cart_id = request.get_signed_cookie('cart_id')
        try:
            cart = Cart.objects.get(cart_id__exact=cart_id)
            items = Item.objects.filter(cart__exact=cart)
            return {'cart_count': items.count()}
        except Exception as ex:
            return {'cart_count': 0,}
    else:
        return {'cart_count': 0,}

from mibandapp.models import Order

def check_order(request):
    if request.user.is_authenticated:
        try:
            orders = Order.objects.filter(user=request.user, is_paid=False)[0]
            if orders:
                return { 'has_pending_order': True, 'order_count': 1, 'uuid': orders.uuid }
            else:
                return {'has_pending_order': False}
        except Exception as ex:
            print(ex)
            return {'has_pending_order': False}
    else:
        return {'has_pending_order': False}

#from __future__ import absolute_import, unicode_literals
import os
from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'microstore.settings'
application = get_wsgi_application()

if __name__ == '__main__':
    from mibandapp.models import Item, Product
    from datetime import datetime, timedelta
    diff = datetime.now() - timedelta(hours=24)
    items = Item.objects.filter(created_at__date__lt=diff, is_paid=False)
    if items:
        for item in items:
            item.product.quantity += item.quantity
            item.product.save()
            item.delete()

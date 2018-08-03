from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from mibandapp.models import Order, Item, Cart, Payment

@shared_task
def send_create_account_email(email, first_name, site_name):
    email_body = render_to_string('email/account_created_email.html', context={'first_name': first_name, 'site_name': site_name})
    email = EmailMultiAlternatives(to=[email], subject='Thank you for signing up!', body=strip_tags(email_body))
    email.attach_alternative(email_body, 'text/html')
    email.send()

@shared_task
def send_order_email(name, email, cart, total, order):
    cart_id = Cart.objects.get(cart_id__exact=cart)
    items = Item.objects.filter(cart=cart_id)
    order = Order.objects.get(pk=order)
    email_body = render_to_string('email/order_created_email.html', context={'first_name': name, 'items': items, 'total': total, 'order': order })
    email = EmailMultiAlternatives(to=[email], subject='Your Order', body=strip_tags(email_body))
    email.attach_alternative(email_body, 'text/html')
    email.send()

@shared_task
def send_payment_recieved_email(name, email, cart, total, order, payment):
    payment = Payment.objects.get(pk=payment)
    order = Order.objects.get(pk=order)
    cart_id = Cart.objects.get(cart_id__exact=cart)
    items = Item.objects.filter(cart=cart_id)
    email_body = render_to_string('email/payment_recieved_email.html', context={'order': order, 'items': items, 'payment': payment})
    email = EmailMultiAlternatives(to=[email], subject='Payment recieved on order: %s' % order.id, body=strip_tags(email_body))
    email.attach_alternative(email_body, 'text/html')
    email.send()

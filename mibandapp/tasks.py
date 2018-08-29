from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from mibandapp.models import Order, Item, Cart, Payment, PushNotification
from pywebpush import webpush, WebPushException, WebPusher
from django.core import serializers
import json
from django.conf import settings
import os

@shared_task
def send_create_account_email(email, first_name, site_name):
    email_body = render_to_string('email/account_created_email.html', context={'first_name': first_name, 'site_name': site_name})
    email = EmailMultiAlternatives(to=[email], subject='Thank you for signing up!', body=strip_tags(email_body))
    email.attach_alternative(email_body, 'text/html')
    email.send()

@shared_task
def send_create_account_email_checkout(email, first_name, password):
    email_body = render_to_string('email/account_created_email_checkout.html', context={'first_name': first_name, 'password': password})
    email = EmailMultiAlternatives(to=[email], subject='We have created an account for you!', body=strip_tags(email_body))
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

@shared_task
def notify_admin_incomplete_payment(order_id, user):
    order = Order.objects.get(pk=order_id)
    user = User.objects.get(id=user)
    payment = Payment.objects.get(order=order)
    email_body = render_to_string('email/incomplete_payment_recieved_email.html', context={'order': order, 'user': user, 'payment': payment })
    email = EmailMultiAlternatives(to=['hello@thelifestylestore.com.ng', 'kenoalords@gmail.com'], subject="ALERT: Incomplete Payment Recieved!", body=strip_tags(email_body))
    email.attach_alternative(email_body, 'text/html')
    email.send()

@shared_task
def send_push_notification(title, url, message):
    subs = PushNotification.objects.all()
    data = {
        "title": title,
        "url": url,
        "message": message,
    }
    # print(data)
    for s in subs:
        try:
            push = json.loads(s.subscription)
            subscription_info={
                 "endpoint": push['endpoint'],
                 "keys": {
                     "p256dh": push['keys']['p256dh'],
                     "auth": push['keys']['auth'],
                 },
             }
            # webpush(
            #     subscription_info,
            #     data='hello',
            #     vapid_private_key='gL1krMw2MRvwTGj8VS-UXZ9FdfOSvLf8nnl8EElGd-M',
            #     vapid_claims={
            #         "sub": "mailto:hello@thelifestylestore.com.ng",
            #         "aud": 'http://127.0.0.1:8000'
            #     },
            # )
            wp = WebPusher(subscription_info)
            wp.send('hello', headers={
                'Authorization': 'WebPush eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJhdWQiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAiLCJleHAiOiIxNTM1MTU3MjcxIiwic3ViIjoibWFpbHRvOmhlbGxvQHRoZWxpZmVzdHlsZXN0b3JlLmNvbS5uZyJ9.nNF82Zt_6K0f87nu6YgM5Fd_JpYGRvK-U554aHqNd8V_gS0d7gaWw9zEGVCZ66Rn-e28xtEkqBeD7GnZE0a3sg',
                'Crypto-Key': 'p256ecdsa=BBVgtyidgfOeXent70LBOtWewZDouTMrfn_2eWBxV5AbpVjgpw9gQvgon07RmCJQ5iDOqn_8FrjmjR16pfn2GJU'
            })
        except WebPushException as ex:
            print("Webpush not successful", ex)
            # Mozilla returns additional information in the body of the response.
            if ex.response and ex.response.json():
                extra = ex.response.json()
                print("Remote service replied with a {}:{}, {}",
                      extra.code,
                      extra.errno,
                      extra.message
                      )

import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, QueryDict, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render, reverse, redirect, render_to_response
from django.views.generic import TemplateView, View, CreateView, DetailView, ListView, FormView, UpdateView
from django.db.models import Sum
from mibandapp.models import Product, Cart, Order, Item, ShippingAddress, Payment, Image, ProductFeature, ProductLike, ProductNotification, ProductSlider, ProductImage, Brand, ShippingZone, State, PushNotification
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from mibandapp.forms import OrderForm, ProductForm, ImageUploadForm, ProductFeaturesFormFormSet, ProductFeatureDetailFormSet, ProductImageFormSet
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from mibandapp.auth_forms import CustomLoginForm, CustomUserCreationForm, CustomPasswordResetForm, CustomSetPasswordForm
from django.utils.text import slugify
from django.utils import timezone
from mibandapp.utils import resize_and_crop
from django.forms import formset_factory, inlineformset_factory
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from mibandapp.tasks import send_create_account_email, send_order_email, send_payment_recieved_email, send_create_account_email_checkout, send_push_notification
import decimal
from django.core import serializers
from pywebpush import webpush

import requests
import json
# Create your views here.

decimal.Context(prec=2, rounding=decimal.ROUND_UP)
# Index View
class IndexView(TemplateView):
    template_name = 'generic/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.featured.all()[:6]
        context['sliders'] = ProductSlider.active.all()
        context['brands'] = Brand.objects.all()[:4]
        return context

class ProductsAll(ListView):
    template_name = './product/all_products.html'
    context_object_name = 'products'
    model = Product
    queryset = Product.active.all()

class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = './parts/account/my_account.html'


class CartView(TemplateView):
    template_name = 'generic/cart.html'

    def post(self, request):
        cart_id = self.request.get_signed_cookie('cart_id')
        quantity = 1
        try:
            quantity = int(self.request.POST.get('quantity'))
        except Exception as ex:
            quantity = 1

        # Verify the product exists
        try:
            product = Product.objects.get(pk=int(self.request.POST.get('pk')))
            print(request.POST)
            if quantity < 1 and quantity > product.quantity:
                messages.error(request, 'You have entered an invalid quantity value for %s, please try again' % product.title)
                if request.is_ajax():
                    return JsonResponse({'status': 'failed', 'message': 'Invalid Quantity'})
                else:
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])
            try:
                cart, created = Cart.objects.get_or_create(cart_id=cart_id)
                if product.quantity - quantity  > 0:
                    try:
                        item = Item.objects.get(cart=cart, product=product)
                        if item:
                            item.quantity += quantity
                            item.save()
                    except ObjectDoesNotExist as ex:
                        item =Item.objects.create(cart=cart, product=product, quantity=quantity)
                    except Exception as ex:
                        print(ex)
                    product.quantity -= quantity
                    product.save()
                    if request.is_ajax():
                        return JsonResponse({ 'status': 'success', 'message': '%s added to cart successfully' % product.title })
                    else:
                        messages.success(request, '<strong>%s</strong> added to cart successfully' % product.title)
                        return HttpResponseRedirect(request.META['HTTP_REFERER'])
                else:
                    if request.is_ajax():
                        return JsonResponse({ 'status': 'failed', 'message': 'Oops! %s is out of stock' % product.title })
                    else:
                        messages.success(request, 'Oops! <strong>%s</strong> is out of stock' % product.title)
                        return HttpResponseRedirect(request.META['HTTP_REFERER'])
            except Exception as ex:
                print(ex)
                if request.is_ajax():
                    return JsonResponse({ 'status': 'failed', 'message': 'We couldn\'t add %s to cart, we might be out of stock' % product.title })
                else:
                    messages.error(request, 'We couldn\'t add %s to cart, we might be out of stock' % product.title)
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])
        except Exception as ex:
            print(ex)
            if request.is_ajax():
                return JsonResponse({ 'status': 'failed', 'message': 'The selected product does not exist' })
            else:
                messages.error(request, 'The selected product does not exist')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    # Handle GET request
    def get(self, request):
        try:
            cart_id = self.request.get_signed_cookie('cart_id')
            cart = Cart.objects.get(cart_id__exact=cart_id)
            items = Item.objects.filter(cart=cart)
            total = [item.product.sale_price * item.quantity for item in items]
            # print(sum(total))
            return render(request, self.template_name, {'items': items, 'total': sum(total)})
        except Exception as ex:
            print(ex)
            return render(request, self.template_name)
            # print(ex)
            # if 'HTTP_REFERER' in request.META:
            #     return HttpResponseRedirect(request.META['HTTP_REFERER'])
            # else:
            #     return HttpResponseRedirect(reverse("microstore:index"))
def validateEmail( email ):
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

class ProductLikeAdd(View):
    def post(self, request, *args, **kwargs):
        product_id = int(request.POST.get('product_id'))
        if product_id != 0:
            try:
                product = Product.objects.get(pk=product_id)
                cookie_id = self.request.get_signed_cookie('_t')
                check_product_like = ProductLike.objects.filter(product=product, cookie_id=cookie_id)
                if check_product_like:
                    if request.user.is_authenticated and request.user.is_superuser:
                        like = ProductLike.objects.create(product=product, cookie_id=cookie_id)
                        like.save()
                        if self.request.is_ajax():
                            count = ProductLike.objects.filter(product=product).count()
                            return JsonResponse({ 'status': True, 'count': count, 'already_liked': False  })
                        else:
                            messages.success(request, 'You liked %s!' % product.title)
                            return HttpResponseRedirect(request.META['HTTP_REFERER'])
                    else:
                        if self.request.is_ajax():
                            count = ProductLike.objects.filter(product=product).count()
                            return JsonResponse({ 'status': False, 'count': count, 'already_liked': True  })
                        else:
                            messages.success(request, 'You liked %s!' % product.title)
                            return HttpResponseRedirect(request.META['HTTP_REFERER'])
                else:
                    like = ProductLike.objects.create(product=product, cookie_id=cookie_id)
                    like.save()
                    if self.request.is_ajax():
                        count = ProductLike.objects.filter(product=product).count()
                        return JsonResponse({ 'status': True, 'count': count, 'already_liked': False })
                    else:
                        messages.success(request, 'You liked %s!' % product.title)
                        return HttpResponseRedirect(request.META['HTTP_REFERER'])
            except Exception as ex:
                print(ex)
                if self.request.is_ajax():
                    return JsonResponse({ 'status': False, 'count': count  })
                else:
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            if self.request.is_ajax():
                return JsonResponse({ 'status': False, 'count': count  })
            else:
                return HttpResponseRedirect(request.META['HTTP_REFERER'])

    def http_method_not_allowed(self, request, *args, **kwargs):
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class ProductSubscribeAdd(View):
    def post(self, request, *args, **kwargs):
        product_id = int(request.POST.get('product_id'))
        email = request.POST['email']
        name = request.POST['fullname'] or None
        redirect = request.META['HTTP_REFERER'] or '/'

        if product_id > 0 and name is None and validateEmail(email):
            try:
                product = Product.objects.get(pk=product_id)
                cookie_id = self.request.get_signed_cookie('_t')
                subscribe = ProductNotification.objects.create(product=product, cookie_id=cookie_id, email=email)
                subscribe.save()
                if self.request.is_ajax():
                    return JsonResponse({ 'status': True, 'message': 'Thank you! You will be notified once this product is available' })
                else:
                    messages.success(request, 'Thank you! we will notify you once <strong>%s</strong> is in stock!' % product.title)
                    return HttpResponseRedirect(redirect)
            except Exception as ex:
                print(ex)
                if self.request.is_ajax():
                    return JsonResponse({ 'status': False, 'message': 'There was a problem with your request, please try again' })
                else:
                    messages.success(request, 'Sorry! Your request was not successful.')
                    return HttpResponseRedirect(redirect)
        else:
            if self.request.is_ajax():
                return JsonResponse({ 'status': False, 'message': 'Oops! something is not right' })
            else:
                messages.success(request, 'Oops! something is not right.')
                return HttpResponseRedirect(redirect)

class PaymentView(TemplateView):
    template_name = 'generic/pay.html'
    order = None

    def get(self, request, *args, **kwargs):
        try:
            self.order = Order.objects.get(uuid__exact=kwargs['order'])
            items = Item.objects.filter(cart=self.order.cart)
            total = sum( [item.product.sale_price * item.quantity for item in items] )
            total += self.order.shipping_cost
            return render(request, self.template_name, { 'order': self.order, 'total': total, 'items': items, 'shipping_cost': self.order.shipping_cost })
        except Exception as ex:
            print(ex)
            return HttpResponseRedirect('/')
        # return render(request, self.template_name)

class DeleteCartItemView(View):
    def post(self, request, *args, **kwargs):
        try:
            cart_id = request.get_signed_cookie('cart_id')
            cart = Cart.objects.get(cart_id__exact=cart_id)
            item = Item.objects.get(cart=cart, pk=self.kwargs['id'])
            product = Product.objects.get(pk=item.product.id)
            product.quantity += item.quantity
            product.save()
            item.delete()
            messages.success(request, '<b>%s</b> removed from cart successfully' % product.title)
            return HttpResponseRedirect(reverse('microstore:cart'))
        except Exception as ex:
            print(ex)
            return HttpResponseRedirect(reverse('microstore:cart'))

    def get(self, request, *args, **kwargs):
        try:
            cookie = request.get_signed_cookie('cart_id')
            cart_id = Cart.objects.get(cart_id__exact=cookie)
            item = Item.objects.get(pk=self.kwargs['id'], cart=cart_id)
            return render(request, template_name='generic/product_delete.html', context={'item': item})
        except Exception as ex:
            return HttpResponseRedirect(reverse('microstore:cart'))

    def http_method_not_allowed(self, request, *args, **kwargs):
        messages.success(request, 'method not allowed')
        return HttpResponseRedirect(reverse('microstore:cart'))

class CheckoutTemplateView(TemplateView):
    template_name = 'generic/checkout.html'
    form = None
    shipping_address = None
    def get(self, request):
        if self.request.user.is_authenticated:
            self.shipping_address = ShippingAddress.objects.filter(user=self.request.user)
        else:
            pass
        try:
            cart_id = self.request.get_signed_cookie('cart_id')
            cart = Cart.objects.get(cart_id__exact=cart_id)
            items = Item.objects.filter(cart=cart)
            total = sum( [item.product.sale_price * item.quantity for item in items] )
            if self.request.user.is_authenticated:
                self.form = OrderForm(initial={ 'first_name': self.request.user.first_name, 'last_name': self.request.user.last_name, 'email': self.request.user.email })
            else:
                self.form = OrderForm()
            return render(request, self.template_name, {'cart': items, 'total': total, 'form': self.form, 'shipping_address': self.shipping_address})
        except Exception as ex:
            print(ex)
            if 'HTTP_REFERER' in request.META:
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            else:
                return HttpResponseRedirect(reverse("microstore:index"))

    def post(self, request):
        cart_id = None
        try:
            cart_id = self.request.get_signed_cookie('cart_id')
        except Exception as ex:
            print(ex)
            return HttpResponseRedirect(reverse('microstore:index'))
        cart = Cart.objects.get(cart_id__exact=cart_id)
        items = Item.objects.filter(cart=cart)
        total = sum( [item.product.sale_price * item.quantity for item in items] )
        form = OrderForm(request.POST)
        user = None
        order_check = None

        try:
            user_id = self.request.get_signed_cookie('_t')
        except Exception as ex:
            print(ex)
            return HttpResponseRedirect(reverse('microstore:index'))

        if not items.exists():
            print('Failed!')
            return HttpResponseRedirect(reverse('microstore:index'))
        if self.request.POST.get('url'):
            return HttpResponseRedirect(reverse('microstore:index'))

        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = User.objects.make_random_password()
            username = slugify(email)
            shipping_cost = calculate_shipping_cost(request, form.cleaned_data['state'].id, cart_id)
            total = decimal.Decimal(shipping_cost['total'])


            # Check if the user is authenticated
            if request.user.is_authenticated:
                self.user = request.user
            else:
                try:
                    # Check if email exists in database then redirect to login page
                    email_check = User.objects.get(email__exact=form.cleaned_data['email'])
                    return redirect(reverse('login') + '?next=%s' % reverse('microstore:checkout'))
                except ObjectDoesNotExist:
                    # User does not exist, automatically create new user account
                    new_user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
                    # Authenticate the new account
                    auth_new_user = authenticate(username=username, password=password)
                    if auth_new_user:
                        send_create_account_email_checkout.delay(email, first_name, password)
                        login(request, auth_new_user)
                        self.user = auth_new_user


            # Check if the order is stale and not paid for
            try:
                order_check = Order.objects.get(cart__cart_id__exact=cart_id)
            except ObjectDoesNotExist as ex:
                pass
            if order_check is not None:
                if order_check.is_paid == False:
                    return redirect(reverse('microstore:pay', kwargs={ 'order': str(order_check.uuid) }))
                return render(request, self.template_name, {'cart': items, 'total': total, 'form': form})
            else:
                # Save the order
                order = form.save(commit=False)
                order.cart = cart
                order.total = total
                order.shipping_cost = shipping_cost['shipping_cost']
                order.user = self.user
                order.save()

                # Save the shipping details for later reference
                street = form.cleaned_data['street']
                city = form.cleaned_data['city']
                state = form.cleaned_data['state']
                phone = form.cleaned_data['phone']

                try:
                    check_shipping = ShippingAddress.objects.get(street__icontains=street, user=self.user)
                except ShippingAddress.DoesNotExist as ex:
                    print(ex)
                    try:
                        add_shipping = ShippingAddress.objects.create(street=street, city=city, state=state, phone=phone, country="NG")
                        add_shipping.user.add(self.user)
                        add_shipping.save()
                    except Exception as ex:
                        print(ex)
                except Exception as ex:
                    pass

                del request.COOKIES['cart_id']
                send_order_email.delay(self.user.first_name, self.user.email, cart.cart_id, total, order.id)
                return redirect(reverse('microstore:pay', kwargs={ 'order': str(order.uuid) }))
        else:
            # Form not valid
            return render(request, self.template_name, {'cart': items, 'total': total, 'form': form})

class GetShippingCost(View):
    def get(self, request, *args, **kwargs):
        try:
            self.cart_id = request.get_signed_cookie('cart_id')
        except Exception as ex:
            if request.is_ajax():
                return JsonResponse({'status': False, 'message': 'No cart found!'})
            else:
                return HttpResponseRedirect(reverse('microstore:checkout'))
        # Get cart items
        return calculate_shipping_cost(request, self.kwargs['state'], self.cart_id)


def calculate_shipping_cost(request, state_id, cart_id):
    state = State.objects.get(id=state_id)
    cart = Cart.objects.get(cart_id__exact=cart_id)
    items = Item.objects.filter(cart=cart)
    if items:
        total_weight = [item.product.weight for item in items]
        total_cost = [item.quantity * item.product.sale_price for item in items]
        weight = sum(total_weight) - decimal.Decimal(0.5)
        total = (weight/decimal.Decimal(0.5) * state.shipping_zone.additional_kg_cost) + state.shipping_zone.kg_cost
        total_due = sum(total_cost) + total
        if request.is_ajax():
            return JsonResponse({ 'status': True, 'shipping_cost': total, 'total': total_due })
        else:
            return { 'shipping_cost': decimal.Decimal(total), 'total': total_due }

class CustomLogoutView(LogoutView):
    next_page = '/'

class CustomLoginView(LoginView):
    model = User
    form_class = CustomLoginForm
    # redirect_authenticated_user = True

class CustomRegisterationView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        next = ''
        # print(form.cleaned_data)
        if 'next' in self.request.GET:
            next = '?next=%s' % self.request.GET.get('next')
        try:
            email_check = User.objects.get(email__exact=email)
            return redirect(reverse("login") + next_link)
        except ObjectDoesNotExist:
            username = slugify(email)
            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name,last_name=last_name)
            if user:
                site = get_current_site(self.request)
                send_create_account_email.delay(email=email, first_name=first_name, site_name=site.name)
                auth_user = authenticate(username=username, password=password)
                if auth_user is not None:
                    login(self.request, auth_user)
                    return HttpResponseRedirect(self.request.GET.get('next') or '/')
                else:
                    return redirect(reverse("login"))

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('reset_password_done')
    email_template_name = 'email/password_reset_email.html'
    html_email_template_name = 'email/password_reset_email.html'
    subject_template_name = 'email/password_reset_email_subject.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    context_object_name = 'form'
    form_class = CustomSetPasswordForm

class CustomPasswordResetCompleteView(TemplateView):
    template_name = 'registration/password_reset_complete.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'
    form_class = CustomSetPasswordForm

# Dashboard views
class DashboardIndex(PermissionRequiredMixin, TemplateView):
    permission_required = ('microstore.can_add_product')
    raise_exception = True
    template_name = 'admin/dashboard.html'
    orders = None
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        self.orders = Order.objects.all().order_by('-created_at')
        context['pending_orders'] = self.orders.filter(is_paid=False).aggregate(total=Sum('total'))
        context['paid_orders'] = self.orders.filter(is_paid=True).aggregate(total=Sum('total'))
        context['orders'] = self.orders[0:5]
        context['total_orders'] = self.orders.count()
        return context

class OrderAllView(PermissionRequiredMixin, ListView):
    permission_required = ('microstore.can_manage_order')
    raise_exception = True
    template_name = 'admin/orders.html'
    model = Order
    context_object_name = 'orders'

class MyOrderView(LoginRequiredMixin, TemplateView):
    template_name = 'parts/order/my_order.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['orders'] = Order.objects.filter(user=self.request.user)
        return context

class OrderSingleView(PermissionRequiredMixin, DetailView):
    permission_required = ('microstore.can_manage_order')
    raise_exception = True
    template_name = 'admin/order_single.html'
    model = Order
    query_pk_and_slug = True
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    context_object_name = 'order'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Item.objects.filter(cart=self.object.cart)
        context['items'] = items
        context['total'] = sum([item.product.sale_price * item.quantity for item in items])
        return context

class PaystackPaymentGateway(View):
    def post(self, request, *args, **kwargs):
        if request.POST['order_id'] is not None:
            order_id = request.POST['order_id']
            secret_key = settings.PAYSTACK_SECRET_KEY
            try:
                order = Order.objects.get(uuid=order_id, is_paid=False)
                amount = int(order.total) * 100
                email = order.email
                headers = {
                    'authorization': 'Bearer ' + secret_key,
                    'content-type': 'application/json',
                    'cache-control': 'no-cache'
                }
                payload = {
                    'email': email,
                    'amount': amount,
                    'order_id': str(order.uuid),
                    'metadata': {
                        'order_id': str(order.uuid)
                    }
                }
                send_request = requests.post(settings.PAYSTACK_API_LINK, json=payload, headers=headers)
                response = json.loads(send_request.text)

                if response['status'] == True:
                    order.transaction_reference = response['data']['reference']
                    order.save()
                    return redirect(response['data']['authorization_url'])
                else:
                    print(response)
                    return redirect(reverse('microstore:pay', kwargs={'order':order.uuid}))

            except Exception as ex:
                print(ex)
                return redirect(request.META['HTTP_REFERER'])

        def http_method_not_allowed(self, request):
            return HttpResponseRedirect(reverse('microstore:index'))

# Confirm payment from paystack
class PaystackPaymentConfirm(View):
    def post(self, request, *args, **kwargs):
        print(request.POST)

    def get(self, request):
        try:
            ref = request.GET['reference']
            if ref is not None:
                headers = {
                    'accepts': 'application/json',
                    'authorization': 'Bearer ' + settings.PAYSTACK_SECRET_KEY,
                    'cache-control': 'no-cache'
                }
                req = requests.get(settings.PAYSTACK_VERIFY_LINK + ref, headers=headers)
                res = json.loads(req.text)
                data = res['data']
                order = Order.objects.get(transaction_reference=data['reference'])
                order.is_paid = True
                order.save()
                if res['status'] == True:
                    amount = data['amount'] / 100
                    payment = Payment(
                        amount= amount,
                        currency= data['currency'],
                        channel= data['channel'],
                        ip_address= data['ip_address'],
                        reference= data['reference'],
                        customer_first_name= data['customer']['first_name'],
                        customer_last_name= data['customer']['last_name'],
                        customer_email= data['customer']['email'],
                        customer_code= data['customer']['customer_code'],
                        customer_id= data['customer']['id'],
                        transaction_date= data['transaction_date'],
                    )
                    payment.order = order
                    payment.save()
                    send_payment_recieved_email.delay(self.request.user.first_name, self.request.user.email, order.cart.cart_id, order.total, order.id, payment.id )
                    if amount == order.total:
                        return redirect(reverse('microstore:thankyou', kwargs={ 'order': str(order.uuid), 'status':'complete' }))
                    else:
                        return redirect(reverse('microstore:thankyou', kwargs={ 'order': str(order.uuid), 'status':'incomplete' } ))
                else:
                    return redirect(reverse('microstore:orderfailed', kwargs={ 'order': str(order.uuid), 'status':'failed' }))
        except Exception as ex:
            print(ex)

# Payment confirmation and thank you page
class PaymentConfirmation(DetailView):
    template_name = 'generic/thank_you.html'
    model = Order
    query_pk_and_slug = True
    slug_field = 'uuid'
    slug_url_kwarg = 'order'
    context_object_name = 'order'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        order = Order.objects.get(uuid__exact=self.object.uuid)
        context['items'] = Item.objects.filter(cart_id__exact=order.cart_id)
        return context

# Payment confirmation failed
class PaymentConfirmationFailed(DetailView):
    template_name = 'generic/failed.html'
    context_object_name = 'order'
    slug_field = 'uuid'
    slug_url_kwarg = 'order'
    model = Order

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        order = Order.objects.get(uuid__exact=self.object.uuid)
        context['items'] = Item.objects.filter(cart_id__exact=order.cart_id)
        return context
#
# Product management
#
class ProductList(PermissionRequiredMixin, ListView):
    permission_required = ('microstore.can_add_product')
    raise_exception = True

    model = Product
    template_name = 'admin/product_list.html'
    context_object_name = 'products'

class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'product/view_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['other_products'] = Product.objects.filter(is_deleted=False).exclude(id=self.kwargs['id'])
        context['images'] = ProductImage.objects.filter(product=self.kwargs['id'])
        return context


# Add Product
class ProductAddSingle(PermissionRequiredMixin, FormView):
    permission_required = ('microstore.can_add_product')
    raise_exception = True
    # permission_denied_message = 'You do not have permission to access this page'

    template_name = 'product/add_product_form.html'
    form_class = ProductForm
    context_object_name = 'form'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['features'] = ProductFeaturesFormFormSet(prefix='features')
        context['details'] = ProductFeatureDetailFormSet(prefix='details')
        context['images'] = ProductImageFormSet(prefix='images')
        return context

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST, request.FILES)
        features = ProductFeaturesFormFormSet(request.POST, prefix="features")
        details = ProductFeatureDetailFormSet(request.POST, request.FILES, prefix="details")
        images = ProductImageFormSet(request.POST, request.FILES, prefix="images")

        if form.is_valid() and features.is_valid() and details.is_valid() and images.is_valid():
            product = form.save(commit=False)
            product.slug = slugify(product.title)
            product.user = request.user
            product.save()

            product_features = features.save(commit=False)
            for pf in product_features:
                pf.product = product
                pf.save()

            product_details = details.save(commit=False)
            for pd in product_details:
                pd.product = product
                pd.save()

            images_uploaded = images.save(commit=False)
            for image in images_uploaded:
                image.product = product
                image.save()

            messages.success(request, '%s has been added successfully' % product.title)
            return redirect(reverse('microstore:products'))
        else:

            # print(form.errors, features.errors, details.errors)
            # return self.form_invalid(form)
            return render(request, template_name=self.template_name, context={'form':form, 'details': details, 'features':features})

class ProductEdit(PermissionRequiredMixin, FormView):
    permission_required = ('microstore.can_add_product')
    raise_exception = True

    template_name = 'product/edit_product_form.html'
    model = Product
    slug_field = 'id'
    slug_url_kwarg = 'id'
    context_object_name = 'form'
    form_class = ProductForm
    success_url = reverse_lazy('microstore:products')
    instance = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = Product.objects.get(id__exact=self.kwargs['id'])
        context['features'] = ProductFeaturesFormFormSet(instance=product, prefix="features")
        context['details'] = ProductFeatureDetailFormSet(instance=product, prefix="details")
        context['images'] = ProductImageFormSet(instance=product, prefix="images")
        context['form'] = ProductForm(instance=product)
        context['product'] = product
        return context

    def post(self, request, *args, **kwargs):
        product = Product.objects.get(id__exact=self.kwargs['id'])
        form = ProductForm(request.POST, request.FILES, instance=product)
        features = ProductFeaturesFormFormSet(request.POST, request.FILES, instance=product, prefix="features")
        details = ProductFeatureDetailFormSet(request.POST, request.FILES, instance=product, prefix="details")
        images = ProductImageFormSet(request.POST, request.FILES, instance=product, prefix="images")

        if form.is_valid() and details.is_valid() and features.is_valid() and images.is_valid():
            features.save()
            details.save()
            images.save()
            product = form.save(commit=False)
            product.slug = slugify(product.title)
            product.save()
            messages.success(request, 'Product updated successfully')
            return redirect(reverse('microstore:products'))
        else:
            return render(request, template_name=self.template_name, context={'form':form, 'details': details, 'features':features, 'images': images, 'product': product})

class ProductDelete(PermissionRequiredMixin, DetailView):
    permission_required = ('microstore.can_add_product')
    raise_exception = True

    template_name = 'product/delete_product.html'
    model = Product
    context_object_name = 'product'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def post(self, request, *args, **kwargs):
        if 'product_id' in request.POST:
            try:
                id = int(request.POST['product_id'])
                product = Product.objects.get(id=id)
                if product:
                    product.is_deleted = True
                    product.deleted_at = timezone.now()
                    product.save()
                    return redirect(reverse('microstore:products'))
                else:
                    return redirect(reverse('microstore:products'))
            except Exception as ex:
                print(ex)
                return redirect(reverse('microstore:products'))


class AboutUsPageView(TemplateView):
    template_name = 'pages/about.html'

class PrivacyPolicyPageView(TemplateView):
    template_name = 'pages/privacy.html'

class ContactUsPageView(TemplateView):
    template_name = 'pages/contact.html'

class ShippingRateJsonView(View):
    def get(self, request, *args, **kwargs):
        state = State.objects.get(pk=self.kwargs['id'])
        zone = ShippingZone.objects.get(pk=state.shipping_zone.id)
        data = {
            'name': zone.name,
            'cost': zone.kg_cost
        }
        return JsonResponse(data)

class ShippingReturnsPageView(TemplateView):
    template_name = 'pages/shipping.html'


class PushNotificationSubcription(View):
    def post(self, request, *args, **kwargs):
        try:
            user = request.get_signed_cookie('_t')
            sub = PushNotification.objects.create(user=user, subscription=request.POST['subscription'])
            sub.save()
            return JsonResponse({'status': True, 'subscribed': True})
        except Exception as ex:
            print(ex)
            return JsonResponse({'status': False})

class FetchPushNotificationSubscriptions(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return JsonResponse({'status': False})

        send_push_notification.delay(request.POST['title'], request.POST['url'], request.POST['message'])
        return JsonResponse({ 'status': True }, safe=False)

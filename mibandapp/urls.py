from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls import url
from mibandapp.views import IndexView, CartView, DeleteCartItemView, CheckoutTemplateView, PaymentView, PaystackPaymentGateway, PaystackPaymentConfirm, PaymentConfirmation, PaymentConfirmationFailed, ProductDetailView, ProductLikeAdd, ProductSubscribeAdd, ProductsAll, AboutUsPageView, PrivacyPolicyPageView, ContactUsPageView, MyOrderView, ShippingRateJsonView, ProfileView, GetShippingCost, ShippingReturnsPageView


app_name = 'microstore'

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('about-us/', AboutUsPageView.as_view(), name="about_us"),
    path('privacy/', PrivacyPolicyPageView.as_view(), name="privacy"),
    path('contact/', ContactUsPageView.as_view(), name="contact"),
    path('shipping-returns/', ShippingReturnsPageView.as_view(), name="shipping_returns"),
    path('cart/', CartView.as_view(), name="cart"),
    path('orders/', MyOrderView.as_view(), name="my_orders"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('cart/<id>/delete', DeleteCartItemView.as_view(), name="remove_cart_item"),
    path('checkout/', CheckoutTemplateView.as_view(), name="checkout"),
    path('checkout/<order>/pay/', PaystackPaymentGateway.as_view(), name='paystack'),
    path('checkout/<order>/', PaymentView.as_view(), name="pay"),
    path('thank-you/<order>/<status>', PaymentConfirmation.as_view(), name="thankyou"),
    path('order-failed/<order>/<status>', PaymentConfirmationFailed.as_view(), name="orderfailed"),
    path('paystack/callback/', PaystackPaymentConfirm.as_view()),
    path('dashboard/', include("mibandapp.admin_urls")),
    path('products/', ProductsAll.as_view(), name="all_products"),
    path('product/<id>/like/', ProductLikeAdd.as_view(), name="like_product"),
    path('product/<id>/subscribe/', ProductSubscribeAdd.as_view(), name="subscribe_product"),
    path('product/<id>/<slug>/', ProductDetailView.as_view(), name="product"),
    # path('shipping/<int:id>/', ShippingRateJsonView.as_view(), name="shipping_rate"),
    path('shipping/<int:state>/', GetShippingCost.as_view(), name="shipping_rate"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""microstore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mibandapp.views import CustomLoginView, CustomLogoutView, CustomRegisterationView, CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView
from django.contrib.auth import views
from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^sw(.*.js)$', TemplateView.as_view(template_name="sw.js", content_type="application/x-javascript"), name="sw"),
    path('', include('mibandapp.urls')),
    path('accounts/login/', CustomLoginView.as_view(), name="login"),
    path('accounts/logout/', CustomLogoutView.as_view(), name="logout"),
    path('accounts/register/', CustomRegisterationView.as_view(), name="register"),
    path('accounts/reset_password/', CustomPasswordResetView.as_view(), name="reset_password"),
    path('accounts/reset_password/done', CustomPasswordResetDoneView.as_view(), name="reset_password_done"),
    path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]

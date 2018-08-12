import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from mibandapp.managers import ActiveProducts, ActiveProductSliders, FeaturedProduct

# Create your models here.
class Image(models.Model):
    image = models.ImageField(upload_to='uploads/')
    is_thumbnail = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def image_url(self):
        return self.image.url

    def thumb_480(self):
        path = self.image.url
        paths = path.split('.')
        return ''.join(paths[:len(paths)-1]) + '_thumb_480x480_.' + paths[-1]

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/")
    is_display = models.BooleanField(default=False)
    is_banner = models.BooleanField(default=False)

    def __str__(self):
        return self.image

class Brand(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="uploads/brands/")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to="uploads/categories/", null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(Category)
    description = models.TextField(max_length=1024, blank=True, null=True)
    regular_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    variants = models.ManyToManyField("self", blank=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, blank=True, default=0.5)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    # Managers
    objects = models.Manager()
    active = ActiveProducts()
    featured = FeaturedProduct()

    def __str__(self):
        return self.title

    def get_image(self):
        image = ProductImage.objects.filter(product=self, is_banner=True)[0]
        return image.image.url

    def get_features(self):
        return ProductFeature.objects.filter(product=self)

    def get_product_details(self):
        return ProductFeatureDetail.objects.filter(product=self)

    def like_count(self):
        return ProductLike.objects.filter(product=self).count()

    class Meta:
        ordering = ['is_deleted', '-created_at']
        permissions = (
            ('can_add_product', 'Can add product'),
        )

class ProductNotification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cookie_id = models.CharField(max_length=128)
    email = models.EmailField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class ProductLike(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cookie_id = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cookie_id

class ProductSlider(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=512)
    image = models.ImageField(upload_to="uploads/")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    active = ActiveProductSliders()

    def __str__(self):
        return self.title

class ProductFeatureDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Cart(models.Model):
    cart_id = models.CharField(max_length=128, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class Item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def total(self):
        return self.product.sale_price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    payer_name = models.CharField(max_length=64, blank=True, null=True)
    payer_email = models.EmailField(max_length=254, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    is_gift = models.BooleanField(default=False)
    first_name = models.CharField(max_length=64, null=True)
    last_name = models.CharField(max_length=64, null=True)
    email = models.EmailField(max_length=64, null=True)
    street = models.CharField(max_length=64, null=True)
    city = models.CharField(max_length=64, null=True)
    state = models.CharField(max_length=64, null=True)
    country = models.CharField(max_length=64, default="NG")
    phone = models.CharField(max_length=64, null=True)
    additional_notes = models.TextField(max_length=1024, null=True, blank=True)
    transaction_reference = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def address(self):
        return "{} {} {}.".format(self.street, self.city, self.state)

    def fullname(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        ordering = ["-created_at"]
        permissions = (
            ('can_manage_order', 'Can manage orders'),
        )

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=6)
    channel = models.CharField(max_length=6)
    ip_address = models.GenericIPAddressField()
    reference = models.CharField(max_length=64)
    customer_first_name = models.CharField(max_length=64, null=True)
    customer_last_name = models.CharField(max_length=64, null=True)
    customer_code = models.CharField(max_length=64)
    customer_email = models.EmailField(max_length=128)
    customer_id = models.IntegerField()
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)


class ShippingAddress(models.Model):
    user = models.ManyToManyField(User)
    street = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)

    def __str__(self):
        return self.street

class ShippingZone(models.Model):
    name = models.CharField(max_length=12)
    kg_cost = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=4)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class State(models.Model):
    name = models.CharField(max_length=64)
    shipping_zone = models.ForeignKey(ShippingZone, on_delete=models.SET_NULL, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class City(models.Model):
    name = models.CharField(max_length=64)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class FeatureList(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    feature = models.ForeignKey(FeatureList, on_delete=models.CASCADE)
    description = models.CharField(max_length=32)

    class Meta:
        ordering = ['feature__name']

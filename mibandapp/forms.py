from django.forms import ModelForm, CharField, EmailField, CheckboxInput, Textarea, IntegerField, TextInput, ImageField, ClearableFileInput, ChoiceField, MultiWidget, MultiValueField, widgets, formset_factory, Form, inlineformset_factory, ModelChoiceField, modelform_factory
from django.utils.translation import gettext_lazy as _
from mibandapp.models import Order, Product, Image, State, City, FeatureList, ProductFeature, ProductFeatureDetail, ProductImage, ProductSlider, Brand, Category
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet, BaseModelFormSet

states = State.objects.all()
# STATE_CHOICES = [[state.name, state.name] for state in states]

class ProductFeaturesForm(ModelForm):
    feature = ModelChoiceField(queryset=FeatureList.objects.all())
    description = CharField(max_length=36)
    description.widget.attrs.update({'class': 'input'})
    class Meta:
        model = ProductFeature
        fields = ('feature', 'description')

class ProductFeaturesFormBaseInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        pass

ProductFeaturesFormFormSet = inlineformset_factory(parent_model=Product, model=ProductFeature, form=ProductFeaturesForm, extra=6, max_num=6)


class OrderForm(ModelForm):
    first_name = CharField(max_length=32)
    last_name = CharField(max_length=32)
    email = EmailField(max_length=128)
    street = CharField(max_length=128)
    city = CharField(max_length=32)
    state = ModelChoiceField(queryset=State.objects.all(), empty_label="Select State")
    phone = CharField(max_length=32)
    additional_notes = CharField(max_length=1024, widget=Textarea, required=False)
    is_gift = CheckboxInput()

    first_name.widget.attrs.update({'class': 'input', 'placeholder': 'First Name'})
    last_name.widget.attrs.update({'class': 'input', 'placeholder': 'Last Name'})
    email.widget.attrs.update({'class': 'input', 'placeholder': 'Email'})
    street.widget.attrs.update({'class': 'input', 'placeholder': 'Street Address'})
    city.widget.attrs.update({'class': 'input', 'placeholder': 'City'})
    phone.widget.attrs.update({'class': 'input', 'placeholder': 'Phone Number'})
    state.widget.attrs.update({'class': 'input', 'placeholder': 'State'})
    additional_notes.widget.attrs.update({'class': 'textarea', 'rows': 3, 'placeholder': 'Enter any additional notes here.'})

    class Meta:
        model = Order
        fields = ('last_name','first_name','city', 'street', 'email', 'phone', 'state', 'additional_notes', 'is_gift')
        labels = {
            'is_gift': _('This is a gift item!')
        }

class ProductForm(ModelForm):
    title = CharField(max_length=64)
    description = CharField(widget=Textarea)
    sale_price = IntegerField()
    regular_price = IntegerField(required=False)
    quantity = IntegerField()
    brand = ModelChoiceField(queryset=Brand.objects.all(), required=False)
    category = ModelChoiceField(queryset=Category.objects.all(), required=False)

    title.widget.attrs.update({'class':'input'})
    sale_price.widget.attrs.update({'class':'input'})
    regular_price.widget.attrs.update({'class':'input'})
    quantity.widget.attrs.update({'class':'input'})
    description.widget.attrs.update({'class':'textarea'})

    class Meta:
        model = Product
        fields = ('title', 'description', 'regular_price', 'sale_price', 'quantity', 'brand', 'category')



    # Form class validators
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('regular_price') is not None:
            if cleaned_data.get('regular_price') < cleaned_data.get('sale_price'):
                error = ValidationError(_('Regular pice cannot be lower than the Sale price'), code='regular_price')
                self.add_error('regular_price', error)

class ProductFeatureDetailForm(ModelForm):
    title = CharField(max_length=128)
    description = CharField(widget=Textarea)

    title.widget.attrs.update({'class':'input'})
    description.widget.attrs.update({'class':'textarea', 'rows':3})
    # title.widget.attrs.update({'class':'input'})
    class Meta:
        exclude = ('created_at', 'is_active',)

ProductFeatureDetailFormSet = inlineformset_factory(parent_model=Product, model=ProductFeatureDetail, extra=3, max_num=3, form=ProductFeatureDetailForm)

class ProductImageUploadForm(ModelForm):
    class Meta:
        model = ProductImage
        fields = ('image', 'is_banner', 'is_display')

ProductImageFormSet = inlineformset_factory(parent_model=Product, model=ProductImage, extra=5, max_num=4, form=ProductImageUploadForm)

class ImageUploadForm(ModelForm):
    class Meta:
        model = Image
        fields = ('image',)

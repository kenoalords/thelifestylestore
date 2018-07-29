from django.forms import TextInput, CharField, PasswordInput, EmailField, EmailInput
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class CustomLoginForm(AuthenticationForm):
    username = CharField(max_length=64, widget=TextInput(attrs={'class': 'input', 'placeholder': 'Username'}))
    password = CharField(max_length=64, widget=PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'}))

    class Meta:
        fields = ('username', 'password')


class CustomUserCreationForm(UserCreationForm):
    email = EmailField(max_length=128, widget=EmailInput(attrs={'class': 'input', 'placeholder': 'E-mail Address'}))
    password1 = CharField(max_length=68, widget=PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'}), label='Enter Password')
    password2 = CharField(max_length=68, widget=PasswordInput(attrs={'class': 'input', 'placeholder': 'Confirm Password'}), label='Confirm Password')
    first_name = CharField(max_length=68, required=True, widget=TextInput(attrs={'class': 'input', 'placeholder': 'First name'}))
    last_name = CharField(max_length=68, required=True, widget=TextInput(attrs={'class': 'input', 'placeholder': 'Last name'}))

    class Meta(UserCreationForm.Meta):
        fields = ('email', 'password1', 'password2')

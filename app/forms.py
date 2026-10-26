from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.forms import EmailInput, TextInput, PasswordInput
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("name", "email")

        widgets = {
            "email": EmailInput(attrs={"autocomplete": "email", "placeholder": "Email address"}),
            "name": TextInput(attrs={"autocomplete": "name", "placeholder": "Full name"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget = PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Create a password"}
        )
        self.fields["password2"].widget = PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Confirm your password"}
        )

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)


class SignInForm(AuthenticationForm):
    username = forms.EmailField(
        widget=EmailInput(attrs={"autocomplete": "email", "placeholder": "Email address"})
    )
    password = forms.CharField(
        strip=False,
        widget=PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "Password"}),
    )


class CheckoutForm(forms.Form):
    phone = forms.CharField(
        max_length=16,
        label="M-Pesa / contact phone",
        widget=TextInput(attrs={"autocomplete": "tel", "placeholder": "07XX XXX XXX"}),
    )
    delivery_address = forms.CharField(
        max_length=255,
        label="Delivery address",
        widget=TextInput(attrs={"autocomplete": "street-address", "placeholder": "Building, street, estate"}),
    )
    county = forms.CharField(
        max_length=100,
        label="County",
        widget=TextInput(attrs={"autocomplete": "address-level1", "placeholder": "e.g. Nairobi"}),
    )
    payment_method = forms.ChoiceField(
        choices=(
            ("mpesa", "M-Pesa (payment confirmation pending)"),
            ("cash_on_delivery", "Cash on delivery"),
        ),
        initial="mpesa",
        widget=forms.RadioSelect,
    )

    def clean_phone(self):
        phone = "".join(character for character in self.cleaned_data["phone"] if character.isdigit() or character == "+")
        local_number = phone.removeprefix("+")
        if local_number.startswith("254"):
            national_number = local_number[3:]
        elif local_number.startswith("0"):
            national_number = local_number[1:]
        else:
            national_number = local_number

        if len(national_number) != 9 or national_number[0] not in "17" or not national_number.isdigit():
            raise forms.ValidationError("Enter a valid Kenyan mobile number, such as 0712 345 678.")
        return f"+254{national_number}"
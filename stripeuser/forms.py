from django import forms

class StripeForm(forms.Form):
    stripe_token = forms.CharField(max_length=256)
from django.shortcuts import render
from .forms import StripeForm
from django.conf import settings
# Create your views here.
from django.views.generic import FormView
from .forms import StripeForm
import stripe
class StripeFormView(FormView):
    form_class = StripeForm
    template_name = "stripeform.html"

    def get_context_data(self, **kwargs):
        context = super(StripeFormView, self).get_context_data(**kwargs)
        context['publishable_key'] = settings.STRIPE_TEST_PUBLIC_KEY
        return context

    def form_valid(self, form):
        customer = stripe.Account.retrieve("acct_1B4q0jKOv9qXOFkx")
        print(form.cleaned_data['stripe_token'])
        customer.external_accounts.create(external_account=form.cleaned_data['stripe_token'])
        return super(StripeFormView, self).form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super(StripeFormView, self).form_invalid(form)
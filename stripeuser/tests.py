from decimal import Decimal
from django.test import TestCase
from djstripe.models import Customer, Charge, Card
from django.contrib.auth.models import User
import stripe
import json
import time
# Create your tests here.
class StripeUserTest(TestCase):
    
    def test_customer_stripe_id(self):
        self.customer = stripe.Customer.create(
            email="aghogho@gmail.com",
            description="customer for aghogho",
        )
        self.assertIsNotNone(self.customer.id)
    
    def test_adding_a_card_to_customer(self):
        kwargs = {"number": 4242424242424242, "cvc":333, "exp_month":8, "exp_year":2018}
        self.token = Card.create_token(**kwargs)
        self.customer.add_card(self.token)
    
    def test_querying_created_user(self):
        customer = Customer.objects.get(subscriber__username='tega')
        self.assertEqual(customer.subscriber.username, 'tega')

    def test_customer_can_be_charged(self):
        #with an account balance of $0 #yes the customer can be charged as long there is a source(card or otherwise link to the account)
        self.assertEqual(self.customer.can_charge(), True, 'customer cant be charged')

    def test_charging_customer(self):
        kwargs = {"currency":"aud"}
        self.customer.charge(Decimal(20), **kwargs)
        self.assertEqual(self.customer.account_balance, -20, "account balance is not -20 it is %s" % (str(self.customer.account_balance),))

    def test_creating_charge(self):
        kwargs = {"amount":20, "currency":"aud","customer":self.customer, "amount_refunded":0}
        self.charge = Charge.objects.create(**kwargs)
        self.assertEqual(self.customer.account_balance, -20, "account balance is not -20 it is %s" % (str(self.customer.account_balance),))
        self.assertEqual(self.charge.failure_code, '', "failure code is '' null, it is %s" % self.charge.failure_code)

class StripeApiTest(TestCase):
    def test_creating_account(self):
        account = stripe.Account.create(
            type="custom",
            country="AU",
            email="esabunor@gmail.com"
        )
    
        accountjson = json.loads(str(account))
        id = accountjson ["id"]
        print(id)
        self.assertIsNotNone(id)

    def test_adding_external_account(self):
        account = stripe.Account.retrieve("acct_1B4q0jKOv9qXOFkx")
        kwargs = {"object":"bank_account","account_number": "000123456", "routing_number":110000, "country":"AU", "currency":"aud"}
        account.external_accounts.create(external_account=kwargs)
        account.save()

    def test_verifying_account(self):
        account = stripe.Account.retrieve("acct_1B4q0jKOv9qXOFkx")
        with open("property2.jpg", "rb") as fp:
            fileupload = stripe.FileUpload.create(
                purpose="identity_document",
                file=fp,
                stripe_account=account.id
            )
        account.legal_entity.dob.day = 19
        account.legal_entity.dob.month = 4
        account.legal_entity.dob.year = 1997
        account.legal_entity.first_name = "tega"
        account.legal_entity.last_name = "esabunor"
        account.legal_entity.type = "individual"
        account.tos_acceptance.date = int(time.time())
        account.tos_acceptance.ip = '8.8.8.8'
        account.legal_entity.address.city = "bentley" 
        account.legal_entity.address.line1 = "31A lawson Street"
        account.legal_entity.address.postal_code = "6102"
        account.legal_entity.address.state = "wa"
        account.legal_entity.verification.document = fileupload.id
        account.save()

    def test_add_source_to_a_customer(self):
        customer = stripe.Customer.retrieve("cus_BRjIE3U26cpZmC")
        kwargs = {"object":"card", "number": 4242424242424242, "cvc":333, "exp_month":8, "exp_year":2018}
        customer.sources.create(source=kwargs) 

    def test_creating_a_new_customer(self):
        customer = stripe.Customer.create(
            email="aghogho@gmail.com",
            description="customer for aghogho",
        )

    def test_charging_customer_with_id(self):
        customer = stripe.Customer.retrieve("cus_BRjIE3U26cpZmC")
        charge = stripe.Charge.create(
            amount=2000,
            currency="aud",
            customer=customer.id,
            description="charging aghogho 2000",
        )
    
    def test_paying_out_account(self):
        account = stripe.Account.retrieve("acct_1B4q0jKOv9qXOFkx")
        account.payout_schedule = {'interval':"manual"}
        stripe.Payout.create(
            amount=1000,
            currency='aud',
            stripe_account=account.id,
        )
    
    def test_paying_out_account_with_customer(self):
        account = stripe.Account.retrieve("acct_1B4q0jKOv9qXOFkx")
        customer = stripe.Customer.retrieve("cus_BRjIE3U26cpZmC")
        charge = stripe.Charge.create(
            amount=2000,
            currency='aud',
            customer=customer.id,
            destination={'account':account.id},
        )

    def test_paying_out_account_with_customer_and_charge(self):
        account = stripe.Account.retrieve("acct_1B4q0jKOv9qXOFkx")
        customer = stripe.Customer.retrieve("cus_BRjIE3U26cpZmC")
        charge = stripe.Charge.create(
            amount=2000,
            currency='aud',
            customer=customer.id,
            destination={'account':account.id},
            application_fee=200,
        )
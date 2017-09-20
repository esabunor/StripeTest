from decimal import Decimal
from django.test import TestCase
from djstripe.models import Customer, Charge, Card
from django.contrib.auth.models import User
from stripe import Payout, Customer, Charge, Recipient, Account
import json
import time
# Create your tests here.
class StripeUserTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='tega', password='N0Password', email='tesabunor@gmail.com')
        self.customer = Customer.create(user)
    
    def test_customer_stripe_id(self):
        self.assertIsNotNone(self.customer.stripe_id)
    
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
    def testAccount(self):
        account = Account.create(
            type="custom",
            country="AU",
            email="esabunor@gmail.com"
        )
    
        accountjson = json.loads(str(account))
        id = accountjson ["id"]
        print(id)
        self.assertIsNotNone(id)

    def test_adding_external_account(self):
        account = Account.create(
            type="custom",
            country="AU",
            email="nukie@gmail.com",
        )
        kwargs = {"object":"card", "number": 42424252174242424242, "cvc":333, "exp_month":8, "exp_year":2018, "currency":"aud", "default_for_currency":True}
        self.token = Card.create_token(**kwargs)
        account.external_accounts.create(external_account=self.token)
        account.legal_entity.dob.day = 19
        account.legal_entity.dob.month = 4
        account.legal_entity.dob.year = 1997
        account.legal_entity.first_name = "tega"
        account.legal_entity.last_name = "esabunor"
        account.legal_entity.type = "individual"
        account.tos_acceptance.date = int(time.time())
        account.tos_acceptance.ip = '8.8.8.8'
        account.save()
        stripe.Payout.create(
            amount=1000,
            currency="aud",
            stripe_account=account.id,
        )

    
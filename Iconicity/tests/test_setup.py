from django.test import TestCase
from django.urls import reverse


class TestSetUp(TestCase):
    def setUp(self):
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.user = {
			'email':'test@gmail.com',
			'password':'123linyu',
		    'username':'test',
		}

        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    
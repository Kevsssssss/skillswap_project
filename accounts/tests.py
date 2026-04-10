from django.test import SimpleTestCase
from django.urls import reverse, resolve
from . import views

class TestAccountsUrls(SimpleTestCase):
    def test_register_url_resolves(self):
        """
        Test that the 'register' URL resolves to the correct view function.
        This will currently fail with AttributeError: module 'accounts.views' has no attribute 'register'
        """
        url = reverse('register')
        self.assertEqual(resolve(url).func, views.register)
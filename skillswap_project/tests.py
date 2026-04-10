from django.test import TestCase
from django.conf import settings
from importlib import import_module

class ServerSetupTests(TestCase):
    def test_asgi_application_is_configured(self):
        """Ensure ASGI_APPLICATION is defined and the application is importable."""
        # 1. Check if the setting exists (This will fail currently)
        self.assertTrue(hasattr(settings, 'ASGI_APPLICATION'), "ASGI_APPLICATION is not set in settings.py")
        
        # 2. Check if the path is valid and importable
        module_path, app_name = settings.ASGI_APPLICATION.rsplit('.', 1)
        try:
            module = import_module(module_path)
            self.assertTrue(hasattr(module, app_name))
        except ImportError:
            self.fail(f"Could not import ASGI module from: {module_path}")
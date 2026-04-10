from django.test import TestCase, Client
from django.contrib.auth.models import User
from marketplace.models import Service

class ProfileDashboardTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_unclaimed_bounty_appears_in_context(self):
        """Test that a posted bounty appears in active_services context."""
        Service.objects.create(
            client=self.user,
            title="Unclaimed Task",
            description="Testing...",
            karma_reward=50
        )
        response = self.client.get('/accounts/profile/')
        
        # Check if the bounty is in the 'active_services' list
        self.assertEqual(len(response.context['active_services']), 1)
        self.assertContains(response, "Unclaimed Task")
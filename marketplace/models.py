from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Service(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_bounties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    karma_reward = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.client.username}"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('CLAIMED', 'Claimed (In Progress)'),
        ('LOCKED', 'Locked (In Escrow)'),
        ('COMPLETED', 'Completed (Paid)'),
        ('CANCELLED', 'Cancelled (Refunded)'),
    ]
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='transactions')
    fulfiller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claimed_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CLAIMED')
    client_approved = models.BooleanField(default=False)
    fulfiller_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.title} - {self.status}"

class KarmaTransaction(models.Model):
    TYPE_CHOICES = [
        ('POST', 'Bounty Posted'), 
        ('REWARD', 'Bounty Reward'), 
        ('REFUND', 'Bounty Refund')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='karma_history')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('transaction', 'reviewer')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    target_url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To: {self.user.username} | From: {self.sender.username if self.sender else 'System'}"

class Message(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} in {self.transaction.service.title}"
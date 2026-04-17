from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse
from .models import Service, Message, Notification


@receiver(post_save, sender=Service)
def broadcast_new_service(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'trading_floor',
            {
                'type': 'service_message',
                'message': {
                    'id': instance.id,
                    'title': instance.title,
                    'provider': instance.client.username,
                    'profile_image_url': instance.client.profile.image.url,
                    'karma_cost': instance.karma_reward,
                    'description': instance.description[:100] + '...'
                }
            }
        )


@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    """Create or update a Notification record whenever a private message is sent."""
    if not created:
        return

    if instance.sender == instance.transaction.service.client:
        recipient = instance.transaction.fulfiller
    else:
        recipient = instance.transaction.service.client

    if recipient is None:
        return

    target_url = reverse('chat_room', kwargs={'pk': instance.transaction.pk})
    
    # Check for existing unread notification from this sender for this specific chat
    existing_notification = Notification.objects.filter(
        user=recipient,
        sender=instance.sender,
        target_url=target_url,
        is_read=False
    ).first()

    if existing_notification:
        # Increment message count or update text
        # We can count messages in the transaction that are newer than when the notification was first created,
        # but for simplicity, let's just count all unread messages or just use a generic message.
        unread_count = Message.objects.filter(
            transaction=instance.transaction,
            sender=instance.sender
        ).count() # This is a bit naive but works for aggregation
        
        existing_notification.message = f"{unread_count} new messages from @{instance.sender.username}"
        existing_notification.save()
    else:
        Notification.objects.create(
            user=recipient,
            sender=instance.sender,
            message=f"New message from @{instance.sender.username}",
            target_url=target_url
        )


@receiver(post_save, sender=Notification)
def send_realtime_notification(sender, instance, created, **kwargs):
    """Trigger the WebSocket toast and sound on creation or update of unread notification."""
    # We want to send a notification if it's new OR if it was just updated and still unread
    if instance.is_read:
        return

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    # Get total unread count for this user
    unread_total = Notification.objects.filter(user=instance.user, is_read=False).count()

    async_to_sync(channel_layer.group_send)(
        f'user_{instance.user.id}_notifications',
        {
            'type': 'send_notification',
            'message': instance.message,
            'sender_id': instance.sender.id if instance.sender else 0,
            'sender_name': instance.sender.username if instance.sender else "System",
            'unread_count': unread_total,
            'target_url': instance.target_url or '#'
        }
    )
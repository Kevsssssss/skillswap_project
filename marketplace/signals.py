print(">>> signals.py loaded <<<")

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
                    'karma_cost': instance.karma_reward,
                    'description': instance.description[:100] + '...'
                }
            }
        )


@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    """Create a Notification record whenever a private message is sent."""
    if not created:
        return

    # FIX: Guard against missing fulfiller (e.g. message created before claim)
    if instance.sender == instance.transaction.service.client:
        recipient = instance.transaction.fulfiller
    else:
        recipient = instance.transaction.service.client

    if recipient is None:
        return

    Notification.objects.create(
        user=recipient,
        sender=instance.sender,
        message=f"New message from @{instance.sender.username}",
        # FIX: reverse() guarantees this matches what chat_room view clears exactly
        target_url=reverse('chat_room', kwargs={'pk': instance.transaction.pk})
    )


@receiver(post_save, sender=Notification)
def send_realtime_notification(sender, instance, created, **kwargs):
    """Trigger the WebSocket toast and sound."""
    if not created:
        return

    # FIX: Guard against missing sender (system notifications)
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    unread_from_sender = Notification.objects.filter(
        user=instance.user,
        sender=instance.sender,
        is_read=False
    ).count()

    async_to_sync(channel_layer.group_send)(
        f'user_{instance.user.id}_notifications',
        {
            'type': 'send_notification',
            'message': instance.message,
            'sender_id': instance.sender.id if instance.sender else 0,
            'sender_name': instance.sender.username if instance.sender else "System",
            'unread_count': unread_from_sender,
            'target_url': instance.target_url or '#'
        }
    )
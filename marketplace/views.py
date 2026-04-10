from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from .models import Service, Transaction, KarmaTransaction, Review, Notification, Message, User
from .forms import ServiceForm, ReviewForm
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q, Avg

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('service_list')
    return render(request, 'marketplace/landing.html')

@login_required
def service_list(request):
    services = Service.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'marketplace/service_list.html', {'services': services})

@login_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    return render(request, 'marketplace/service_detail.html', {'service': service})

@login_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            reward = form.cleaned_data.get('karma_reward')
            profile_obj = request.user.profile
            if profile_obj.karma_balance < reward:
                messages.error(request, "Insufficient Karma.")
                return render(request, 'marketplace/service_form.html', {'form': form})
            try:
                with transaction.atomic():
                    profile_obj.karma_balance -= reward
                    profile_obj.save()
                    KarmaTransaction.objects.create(
                        user=request.user, amount=-reward,
                        transaction_type='POST',
                        description=f"Funded: {form.cleaned_data.get('title')}"
                    )
                    service = form.save(commit=False)
                    service.client = request.user
                    service.save()
                messages.success(request, 'Bounty posted!')
                return redirect('service_list')
            except Exception:
                messages.error(request, "System error.")
    else:
        form = ServiceForm()
    return render(request, 'marketplace/service_form.html', {'form': form})

@login_required
def claim_bounty(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    if service.client == request.user:
        messages.error(request, "Cannot claim your own bounty.")
        return redirect('service_detail', pk=pk)

    with transaction.atomic():
        tx = Transaction.objects.create(service=service, fulfiller=request.user, status='LOCKED')
        service.is_active = False
        service.save()
        Notification.objects.create(
            user=service.client,
            sender=request.user,
            message=f"@{request.user.username} claimed your bounty: {service.title}",
            target_url=f"/marketplace/chat/{tx.pk}/"
        )
    messages.success(request, "Bounty claimed!")
    return redirect('chat_room', pk=tx.pk)

@login_required
def profile(request):
    unclaimed_listings = Service.objects.filter(client=request.user, is_active=True)
    bounties_in_progress = Transaction.objects.filter(service__client=request.user).exclude(status='COMPLETED')
    tasks_im_doing = Transaction.objects.filter(fulfiller=request.user).exclude(status='COMPLETED')
    completed_tasks = Transaction.objects.filter(Q(service__client=request.user) | Q(fulfiller=request.user), status='COMPLETED')
    
    for tx in completed_tasks:
        tx.user_has_reviewed = Review.objects.filter(transaction=tx, reviewer=request.user).exists()
        
    karma_history = KarmaTransaction.objects.filter(user=request.user).order_by('-created_at')
    
    # THE STABLE ROLLBACK: Just fetch raw unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    avg_rating = Review.objects.filter(reviewee=request.user).aggregate(Avg('rating'))['rating__avg']

    return render(request, 'accounts/profile.html', {
        'unclaimed_listings': unclaimed_listings,
        'bounties_in_progress': bounties_in_progress,
        'tasks_im_doing': tasks_im_doing,
        'completed_tasks': completed_tasks,
        'karma_history': karma_history,
        'notifications': notifications, # Restored raw variable
        'avg_rating': avg_rating,
    })

@login_required
def chat_room(request, pk):
    transaction_obj = get_object_or_404(Transaction, pk=pk)
    if request.user not in [transaction_obj.service.client, transaction_obj.fulfiller]:
        return redirect('profile')

    Notification.objects.filter(
        user=request.user,
        target_url__icontains=f'/marketplace/chat/{pk}/',
        is_read=False
    ).update(is_read=True)

    return render(request, 'marketplace/chat_room.html', {
        'transaction': transaction_obj,
        'chat_messages': transaction_obj.messages.all()
    })

@login_required
def upload_file(request, pk):
    if request.method == 'POST' and request.FILES.get('chat_file'):
        transaction_obj = get_object_or_404(Transaction, pk=pk)
        uploaded_file = request.FILES['chat_file']
        message = Message.objects.create(
            transaction=transaction_obj, sender=request.user,
            content=f"Sent a file: {uploaded_file.name}", file=uploaded_file
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{pk}',
            {
                'type': 'chat_message',
                'message': message.content,
                'sender': request.user.username,
                'file_url': message.file.url,
                'is_image': message.file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
            }
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@login_required
def inbox(request):
    my_chats = Transaction.objects.filter(Q(service__client=request.user) | Q(fulfiller=request.user)).order_by('-updated_at')
    for tx in my_chats:
        tx.unread_count = Notification.objects.filter(user=request.user, target_url__icontains=f'/marketplace/chat/{tx.pk}/', is_read=False).count()
    return render(request, 'marketplace/inbox.html', {'my_chats': my_chats})

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user).delete()
    # The fix: Append the hash to tell the browser which tab we want
    return redirect(reverse('profile') + '#alerts')

@login_required
def mark_transaction_complete(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    if request.user not in [tx.fulfiller, tx.service.client]: return redirect('profile')

    if request.user == tx.service.client:
        tx.client_approved = True
        Notification.objects.create(
            user=tx.fulfiller, sender=request.user,
            message=f"Client approved work for: {tx.service.title}",
            target_url=f"/marketplace/chat/{tx.pk}/"
        )
    else:
        tx.fulfiller_approved = True
        Notification.objects.create(
            user=tx.service.client, sender=request.user,
            message=f"Worker marked as done: {tx.service.title}",
            target_url=f"/marketplace/chat/{tx.pk}/"
        )
    tx.save()

    if tx.client_approved and tx.fulfiller_approved:
        with transaction.atomic():
            tx.status = 'COMPLETED'
            tx.save()
            worker_profile = tx.fulfiller.profile
            worker_profile.karma_balance += tx.service.karma_reward
            worker_profile.save()
            KarmaTransaction.objects.create(
                user=tx.fulfiller, amount=tx.service.karma_reward,
                transaction_type='REWARD', description=f"Earned from: {tx.service.title}"
            )
            Notification.objects.create(user=tx.fulfiller, message=f"Payment received! +{tx.service.karma_reward} Karma.")
        messages.success(request, "Task complete!")
    return redirect('profile')

@login_required
def cancel_bounty(request, pk):
    service = get_object_or_404(Service, pk=pk, client=request.user, is_active=True)
    with transaction.atomic():
        p = request.user.profile
        p.karma_balance += service.karma_reward
        p.save()
        KarmaTransaction.objects.create(user=request.user, amount=service.karma_reward, transaction_type='REFUND', description=f"Refund: {service.title}")
        service.is_active = False
        service.save()
    return redirect('profile')

@login_required
def submit_review(request, transaction_pk):
    tx = get_object_or_404(Transaction, pk=transaction_pk, status='COMPLETED')
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.transaction, review.reviewer = tx, request.user
            review.reviewee = tx.fulfiller if request.user == tx.service.client else tx.service.client
            review.save()
            return redirect('profile')
    return render(request, 'marketplace/review_form.html', {'form': ReviewForm(), 'transaction': tx})

@login_required
def clear_single_alert(request, pk):
    Notification.objects.filter(pk=pk, user=request.user).delete()
    return redirect(reverse('profile') + '#alerts') 
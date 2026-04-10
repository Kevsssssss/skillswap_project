from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from marketplace.models import Transaction, Service, KarmaTransaction, Review, Notification

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    finished_statuses = ['COMPLETED', 'CANCELLED']

    # 1. Active Bounties I created (Client)
    bounties_in_progress = Transaction.objects.filter(
        service__client=request.user
    ).exclude(status__in=finished_statuses).order_by('-created_at')

    # 2. Unclaimed Bounties I created
    unclaimed_listings = request.user.posted_bounties.filter(
        is_active=True
    ).order_by('-created_at')

    # 3. Tasks I am currently doing (Worker)
    tasks_im_doing = request.user.claimed_tasks.exclude(
        status__in=finished_statuses
    ).order_by('-created_at')

    # 4. Completed Tasks for Reviews
    completed_tasks = Transaction.objects.filter(
        status='COMPLETED'
    ).filter(
        Q(service__client=request.user) | Q(fulfiller=request.user)
    ).order_by('-updated_at')

    for tx in completed_tasks:
        tx.user_has_reviewed = Review.objects.filter(
            transaction=tx, 
            reviewer=request.user
        ).exists()

    # 5. Rating & Karma History
    karma_history = request.user.karma_history.all().order_by('-created_at')[:10]
    
    # 6. Full Notification History
    notifications = request.user.notifications.all().order_by('-created_at')

    avg_rating = request.user.reviews_received.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)

    context = {
        'bounties_in_progress': bounties_in_progress,
        'unclaimed_listings': unclaimed_listings,
        'tasks_im_doing': tasks_im_doing,
        'completed_tasks': completed_tasks,
        'karma_history': karma_history,
        'notifications': notifications, # Full history for the tab
        'avg_rating': avg_rating,
    }
    return render(request, 'accounts/profile.html', context)
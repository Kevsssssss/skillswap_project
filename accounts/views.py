from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from marketplace.models import Transaction, Service, KarmaTransaction, Review, Notification
from django.contrib.auth.models import User
from .forms import UserUpdateForm, ProfileUpdateForm

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

    avg_rating_raw = request.user.reviews_received.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating_raw, 1) if avg_rating_raw is not None else None
    review_count = request.user.reviews_received.count()

    context = {
        'bounties_in_progress': bounties_in_progress,
        'unclaimed_listings': unclaimed_listings,
        'tasks_im_doing': tasks_im_doing,
        'completed_tasks': completed_tasks,
        'karma_history': karma_history,
        'notifications': notifications,
        'avg_rating': avg_rating,
        'review_count': review_count,
    }
    return render(request, 'accounts/profile.html', context)

def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    
    avg_rating_raw = user.reviews_received.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating_raw, 1) if avg_rating_raw is not None else None
    review_count = user.reviews_received.count()
    
    # Show their active bounties
    active_bounties = user.posted_bounties.filter(is_active=True).order_by('-created_at')

    context = {
        'profile_user': user,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'active_bounties': active_bounties,
    }
    return render(request, 'accounts/public_profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/edit_profile.html', context)

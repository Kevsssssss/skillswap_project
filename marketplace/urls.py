from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('inbox/', views.inbox, name='inbox'), # NEW
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('create/', views.service_create, name='service_create'),
    path('<int:pk>/claim/', views.claim_bounty, name='claim_bounty'),
    path('transaction/<int:pk>/complete/', views.mark_transaction_complete, name='mark_transaction_complete'),
    path('<int:pk>/cancel/', views.cancel_bounty, name='cancel_bounty'),
    path('transaction/<int:transaction_pk>/review/', views.submit_review, name='submit_review'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('transaction/<int:pk>/chat/', views.chat_room, name='chat_room'),
    path('transaction/<int:pk>/upload/', views.upload_file, name='upload_file'),
    path('alert/<int:pk>/clear/', views.clear_single_alert, name='clear_single_alert'),
]
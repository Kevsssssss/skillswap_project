from django.contrib import admin
from .models import Service, Transaction

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'karma_reward', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'client__username')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'fulfiller', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('fulfiller__username', 'service__title', 'service__client__username')
    readonly_fields = ('created_at', 'updated_at')
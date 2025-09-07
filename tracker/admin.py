
"""
Admin configuration for the tracker app.
"""
from django.contrib import admin
from .models import EthereumAddress, WatchList, Transaction, Alert, AddressWatchList


@admin.register(EthereumAddress)
class EthereumAddressAdmin(admin.ModelAdmin):
    """Admin interface for EthereumAddress model."""
    list_display = ['address', 'label', 'balance', 'is_contract', 'last_updated']
    list_filter = ['is_contract', 'created_at']
    search_fields = ['address', 'label']
    readonly_fields = ['created_at', 'last_updated']


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    """Admin interface for WatchList model."""
    list_display = ['name', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""
    list_display = ['hash', 'from_address', 'to_address', 'value', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['hash', 'from_address__address', 'to_address__address']
    readonly_fields = ['hash', 'timestamp']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin interface for Alert model."""
    list_display = ['user', 'address', 'alert_type', 'threshold', 'is_active']
    list_filter = ['alert_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'address__address']


@admin.register(AddressWatchList)
class AddressWatchListAdmin(admin.ModelAdmin):
    """Admin interface for AddressWatchList through model."""
    list_display = ['address', 'watchlist', 'added_at']
    list_filter = ['added_at']
    search_fields = ['address__address', 'watchlist__name']


from django.contrib import admin

# Register your models here.

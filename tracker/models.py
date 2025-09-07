"""Models
for the Ethereum address tracker application.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EthereumAddress(models.Model):
    """Model representing an Ethereum address being tracked."""
    address = models.CharField(max_length=42, unique=True)
    label = models.CharField(max_length=100, blank=True)
    balance = models.DecimalField(max_digits=30, decimal_places=18, default=0)
    last_updated = models.DateTimeField(default=timezone.now)
    is_contract = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Many-to-many relationship with WatchList
    watchlists = models.ManyToManyField(WatchList, through='AddressWatchList', blank=True)

    def __str__(self):
        return self.label if self.label else self.address[:10] + "..."


class AddressWatchList(models.Model):
    """Through model for the many-to-many relationship between Address and WatchList."""
    address = models.ForeignKey(EthereumAddress, on_delete=models.CASCADE)
    watchlist = models.ForeignKey(WatchList, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['address', 'watchlist']

    def __str__(self):
        return f"{self.address} in {self.watchlist.name}"


class Transaction(models.Model):

    hash = models.CharField(max_length=66, unique=True)
    from_address = models.ForeignKey(
        EthereumAddress,
        on_delete=models.CASCADE,
        related_name='outgoing_transactions'
    )
    to_address = models.ForeignKey(
        EthereumAddress,
        on_delete=models.CASCADE,
        related_name='incoming_transactions'
    )
    value = models.DecimalField(max_digits=30, decimal_places=18)
    gas_price = models.BigIntegerField()
    gas_used = models.BigIntegerField()
    block_number = models.BigIntegerField()
    timestamp = models.DateTimeField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Tx: {self.hash[:10]}... - {self.value} ETH"



class Alert(models.Model):

    ALERT_TYPES = [
        ('balance', 'Balance Change'),
        ('transaction', 'New Transaction'),
        ('large_transaction', 'Large Transaction'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    address = models.ForeignKey(EthereumAddress, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold = models.DecimalField(max_digits=30, decimal_places=18, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.alert_type} alert for {self.address} by {self.user.username}"


from django.db import models



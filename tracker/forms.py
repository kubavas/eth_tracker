
"""
Forms for the Ethereum address tracker application.
"""
from django import forms
from .models import EthereumAddress, WatchList, Alert
import re


class AddAddressForm(forms.ModelForm):
    """Form for adding a new Ethereum address to track."""

    class Meta:
        model = EthereumAddress
        fields = ['address', 'label']
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0x...',
                'required': True
            }),
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional label for this address'
            })
        }

    def clean_address(self):
        """Validate Ethereum address format."""
        address = self.cleaned_data['address']
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            raise forms.ValidationError('Invalid Ethereum address format')
        return address.lower()


class CreateWatchListForm(forms.ModelForm):
    """Form for creating a new watchlist."""

    class Meta:
        model = WatchList
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }


class CreateAlertForm(forms.ModelForm):
    """Form for creating address alerts."""

    class Meta:
        model = Alert
        fields = ['address', 'alert_type', 'threshold']
        widgets = {
            'address': forms.Select(attrs={'class': 'form-control'}),
            'alert_type': forms.Select(attrs={'class': 'form-control'}),
            'threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            })
        }

    def __init__(self, user, *args, **kwargs):
        """Initialize form with user's addresses."""
        super().__init__(*args, **kwargs)
        self.fields['address'].queryset = EthereumAddress.objects.filter(
            watchlists__user=user
        ).distinct()



```python
"""
Tests for the Ethereum address tracker application.
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import EthereumAddress, WatchList, Transaction, Alert
from .forms import AddAddressForm


class EthereumAddressModelTest(TestCase):
    """Test cases for EthereumAddress model."""

    def setUp(self):
        """Set up test data."""
        self.address = EthereumAddress.objects.create(
            address='0x1234567890123456789012345678901234567890',
            label='Test Address',
            balance=Decimal('10.5')
        )

    def test_address_str_with_label(self):
        """Test string representation with label."""
        self.assertEqual(str(self.address), 'Test Address')

    def test_address_str_without_label(self):
        """Test string representation without label."""
        self.address.label = ''
        self.assertEqual(str(self.address), '0x12345678...')


class WatchListModelTest(TestCase):
    """Test cases for WatchList model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password')
        self.watchlist = WatchList.objects.create(
            name='Test List',
            description='Test Description',
            user=self.user
        )

    def test_watchlist_str(self):
        """Test string representation of watchlist."""
        self.assertEqual(str(self.watchlist), 'Test List - testuser')


class AddAddressFormTest(TestCase):
    """Test cases for AddAddressForm."""

    def test_valid_address(self):
        """Test form with valid Ethereum address."""
        form_data = {
            'address': '0x1234567890123456789012345678901234567890',
            'label': 'Test Address'
        }
        form = AddAddressForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_address(self):
        """Test form with invalid Ethereum address."""
        form_data = {
            'address': 'invalid_address',
            'label': 'Test Address'
        }
        form = AddAddressForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Invalid Ethereum address format', form.errors['address'])


class HomeViewTest(TestCase):
    """Test cases for home view."""

    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password')

        # Create test addresses
        self.addr1 = EthereumAddress.objects.create(
            address='0x1111111111111111111111111111111111111111',
            balance=Decimal('50.0')
        )
        self.addr2 = EthereumAddress.objects.create(
            address='0x2222222222222222222222222222222222222222',
            balance=Decimal('25.0')
        )

    def test_home_view_status_code(self):
        """Test that home view returns 200 status code."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        """Test that home view uses correct template."""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

    def test_home_view_context(self):
        """Test that home view provides correct context."""
        response = self.client.get(reverse('home'))
        self.assertIn('recent_transactions', response.context)
        self.assertIn('top_addresses', response.context)


class AddressDetailViewTest(TestCase):
    """Test cases for address detail view."""

    def setUp(self):
        """Set up test data."""
        self.address = EthereumAddress.objects.create(
            address='0x1234567890123456789012345678901234567890',
            label='Test Address'
        )

    def test_address_detail_view_status_code(self):
        """Test that address detail view returns 200 for valid address."""
        response = self.client.get(
            reverse('address_detail', args=[self.address.address])
        )
        self.assertEqual(response.status_code, 200)

    def test_address_detail_view_404(self):
        """Test that address detail view returns 404 for invalid address."""
        response = self.client.get(
            reverse('address_detail', args=['0xnonexistent'])
        )
        self.assertEqual(response.status_code, 404)


class DashboardViewTest(TestCase):
    """Test cases for dashboard view (login required)."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password')
        self.watchlist = WatchList.objects.create(
            name='Test List',
            user=self.user
        )

    def test_dashboard_requires_login(self):
        """Test that dashboard redirects non-authenticated users."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_authenticated_access(self):
        """Test that authenticated users can access dashboard."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')


class AddAddressViewTest(TestCase):
    """Test cases for add address view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password')

    def test_add_address_requires_login(self):
        """Test that add address view requires authentication."""
        response = self.client.get(reverse('add_address'))
        self.assertEqual(response.status_code, 302)

    def test_add_address_get_request(self):
        """Test GET request to add address view."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('add_address'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_add_address_post_valid(self):
        """Test POST request with valid address data."""
        self.client.login(username='testuser', password='password')
        data = {
            'address': '0x1234567890123456789012345678901234567890',
            'label': 'Test Address'
        }
        response = self.client.post(reverse('add_address'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Check that address was created
        self.assertTrue(
            EthereumAddress.objects.filter(
                address='0x1234567890123456789012345678901234567890'
            ).exists()
        )

    def test_add_address_post_invalid(self):
        """Test POST request with invalid address data."""
        self.client.login(username='testuser', password='password')
        data = {
            'address': 'invalid_address',
            'label': 'Test Address'
        }
        response = self.client.post(reverse('add_address'), data)
        self.assertEqual(response.status_code, 200)  # Stay on form page
        self.assertFormError(response, 'form', 'address', 'Invalid Ethereum address format')


@pytest.mark.django_db
class TestModels:
    """Pytest test class for models."""

    def test_ethereum_address_creation(self):
        """Test creating an Ethereum address."""
        address = EthereumAddress.objects.create(
            address='0x1234567890123456789012345678901234567890',
            label='Pytest Address'
        )
        assert address.address == '0x1234567890123456789012345678901234567890'
        assert address.label == 'Pytest Address'
        assert str(address) == 'Pytest Address'

    def test_watchlist_creation(self):
        """Test creating a watchlist."""
        user = User.objects.create_user('testuser', 'test@test.com', 'password')
        watchlist = WatchList.objects.create(
            name='Pytest List',
            user=user
        )
        assert watchlist.name == 'Pytest List'
        assert watchlist.user == user
        assert str(watchlist) == 'Pytest List - testuser'

    def test_many_to_many_relationship(self):
        """Test many-to-many relationship between Address and WatchList."""
        user = User.objects.create_user('testuser', 'test@test.com', 'password')
        watchlist = WatchList.objects.create(name='Test List', user=user)
        address = EthereumAddress.objects.create(
            address='0x1234567890123456789012345678901234567890'
        )

        watchlist.ethereumaddress_set.add(address)

        assert address in watchlist.ethereumaddress_set.all()
        assert watchlist in address.watchlists.all()


```
from django.test import TestCase

# Create your tests here.

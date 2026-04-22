import unittest
from unittest.mock import patch, MagicMock
import hashlib
from datetime import datetime, timedelta
from marketplace import Marketplace


class TestMarketplace(unittest.TestCase):
    """Test suite for the Marketplace class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.marketplace = Marketplace()
        self.test_username = "testuser"
        self.test_email = "test@example.com"
        self.test_password = "password123"
    
    def tearDown(self):
        """Clean up after each test method."""
        self.marketplace = None
    
    # Test user registration
    def test_register_user_success(self):
        """Test successful user registration."""
        result = self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        self.assertTrue(result)
        self.assertIn(self.test_username, self.marketplace.users)
        
        user_data = self.marketplace.users[self.test_username]
        self.assertEqual(user_data['email'], self.test_email)
        self.assertEqual(user_data['fiat_balance'], 0.0)
        self.assertEqual(user_data['crypto_balances']['BTC'], 0.0)
        self.assertEqual(user_data['crypto_balances']['ETH'], 0.0)
        self.assertEqual(user_data['crypto_balances']['SOL'], 0.0)
    
    def test_register_user_duplicate_username(self):
        """Test registration fails with duplicate username."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        result = self.marketplace.register_user(
            self.test_username, 
            "different@example.com", 
            "different_password"
        )
        self.assertFalse(result)
    
    def test_register_user_duplicate_email(self):
        """Test registration fails with duplicate email."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        result = self.marketplace.register_user(
            "different_user", 
            self.test_email, 
            "different_password"
        )
        self.assertFalse(result)
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password"
        expected_hash = hashlib.sha256(password.encode()).hexdigest()
        actual_hash = self.marketplace._hash_password(password)
        self.assertEqual(expected_hash, actual_hash)
    
    # Test user authentication
    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        result = self.marketplace.authenticate_user(
            self.test_username, 
            self.test_password
        )
        self.assertTrue(result)
    
    def test_authenticate_user_wrong_password(self):
        """Test authentication fails with wrong password."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        result = self.marketplace.authenticate_user(
            self.test_username, 
            "wrong_password"
        )
        self.assertFalse(result)
    
    def test_authenticate_user_nonexistent(self):
        """Test authentication fails for nonexistent user."""
        result = self.marketplace.authenticate_user(
            "nonexistent_user", 
            "password"
        )
        self.assertFalse(result)
    
    # Test symbol validation
    def test_validate_symbol_valid(self):
        """Test validation of supported symbols."""
        self.assertTrue(self.marketplace._validate_symbol('BTC'))
        self.assertTrue(self.marketplace._validate_symbol('ETH'))
        self.assertTrue(self.marketplace._validate_symbol('SOL'))
        self.assertTrue(self.marketplace._validate_symbol('btc'))
    
    def test_validate_symbol_invalid(self):
        """Test validation rejects unsupported symbols."""
        self.assertFalse(self.marketplace._validate_symbol('DOGE'))
        self.assertFalse(self.marketplace._validate_symbol('XRP'))
    
    # Test get user balances
    def test_get_user_balances_success(self):
        """Test retrieving user balances."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        balances = self.marketplace.get_user_balances(self.test_username)
        
        self.assertIsNotNone(balances)
        self.assertEqual(balances['fiat_balance'], 0.0)
        self.assertIn('crypto_balances', balances)
        self.assertEqual(balances['crypto_balances']['BTC'], 0.0)
    
    def test_get_user_balances_nonexistent_user(self):
        """Test getting balances for nonexistent user returns None."""
        balances = self.marketplace.get_user_balances("nonexistent_user")
        self.assertIsNone(balances)
    
    # Test fiat deposit
    def test_deposit_fiat_success(self):
        """Test successful fiat deposit."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        result = self.marketplace.deposit_fiat(self.test_username, 1000.0)
        
        self.assertTrue(result)
        self.assertEqual(
            self.marketplace.users[self.test_username]['fiat_balance'], 
            1000.0
        )
        self.assertEqual(
            self.marketplace.users[self.test_username]['total_deposits'], 
            1000.0
        )
        self.assertEqual(len(self.marketplace.transactions), 1)
        self.assertEqual(
            self.marketplace.transactions[0]['type'], 
            'DEPOSIT'
        )
    
    def test_deposit_fiat_negative_amount(self):
        """Test deposit fails with negative amount."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        result = self.marketplace.deposit_fiat(self.test_username, -100.0)
        self.assertFalse(result)
    
    def test_deposit_fiat_zero_amount(self):
        """Test deposit fails with zero amount."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        result = self.marketplace.deposit_fiat(self.test_username, 0.0)
        self.assertFalse(result)
    
    def test_deposit_fiat_nonexistent_user(self):
        """Test deposit fails for nonexistent user."""
        result = self.marketplace.deposit_fiat("nonexistent_user", 100.0)
        self.assertFalse(result)
    
    def test_deposit_fiat_multiple_deposits(self):
        """Test multiple deposits accumulate correctly."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        self.marketplace.deposit_fiat(self.test_username, 500.0)
        self.marketplace.deposit_fiat(self.test_username, 300.0)
        
        self.assertEqual(
            self.marketplace.users[self.test_username]['fiat_balance'], 
            800.0
        )
        self.assertEqual(
            self.marketplace.users[self.test_username]['total_deposits'], 
            800.0
        )
    
    # Test fiat withdrawal
    def test_withdraw_fiat_success(self):
        """Test successful fiat withdrawal."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        self.marketplace.deposit_fiat(self.test_username, 1000.0)
        result = self.marketplace.withdraw_fiat(self.test_username, 300.0)
        
        self.assertTrue(result)
        self.assertEqual(
            self.marketplace.users[self.test_username]['fiat_balance'], 
            700.0
        )
        self.assertEqual(
            self.marketplace.users[self.test_username]['total_withdrawals'], 
            300.0
        )
    
    def test_withdraw_fiat_insufficient_balance(self):
        """Test withdrawal fails with insufficient balance."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        self.marketplace.deposit_fiat(self.test_username, 500.0)
        result = self.marketplace.withdraw_fiat(self.test_username, 600.0)
        
        self.assertFalse(result)
        self.assertEqual(
            self.marketplace.users[self.test_username]['fiat_balance'], 
            500.0
        )
    
    def test_withdraw_fiat_negative_amount(self):
        """Test withdrawal fails with negative amount."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        result = self.marketplace.withdraw_fiat(self.test_username, -100.0)
        self.assertFalse(result)
    
    def test_withdraw_fiat_nonexistent_user(self):
        """Test withdrawal fails for nonexistent user."""
        result = self.marketplace.withdraw_fiat("nonexistent_user", 100.0)
        self.assertFalse(result)
    
    # Test crypto price fetching
    @patch('urllib.request.urlopen')
    def test_get_crypto_price_success(self, mock_urlopen):
        """Test successful crypto price fetching."""
        mock_html = '<html><body>Price: $45,678.90</body></html>'
        mock_response = MagicMock()
        mock_response.read.return_value = mock_html.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        price = self.marketplace.get_crypto_price('BTC')
        self.assertIsNotNone(price)
        self.assertEqual(price, 45678.90)
    
    @patch('urllib.request.urlopen')
    def test_get_crypto_price_caching(self, mock_urlopen):
        """Test price caching functionality."""
        mock_html = '<html><body>Price: $45,678.90</body></html>'
        mock_response = MagicMock()
        mock_response.read.return_value = mock_html.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        price1 = self.marketplace.get_crypto_price('BTC')
        self.assertEqual(mock_urlopen.call_count, 1)
        
        price2 = self.marketplace.get_crypto_price('BTC')
        self.assertEqual(mock_urlopen.call_count, 1)
        self.assertEqual(price1, price2)
    
    def test_get_crypto_price_invalid_symbol(self):
        """Test price fetching with invalid symbol."""
        price = self.marketplace.get_crypto_price('INVALID')
        self.assertIsNone(price)
    
    @patch('urllib.request.urlopen')
    def test_get_crypto_price_network_error(self, mock_urlopen):
        """Test price fetching handles network errors."""
        mock_urlopen.side_effect = Exception("Network error")
        
        price = self.marketplace.get_crypto_price('BTC')
        # Falls back to configured dummy price when there is no cache
        self.assertEqual(price, 75744.77)
    
    @patch('urllib.request.urlopen')
    def test_get_crypto_price_fallback_to_cache(self, mock_urlopen):
        """Test fallback to cached price on network error."""
        mock_html = '<html><body>Price: $45,678.90</body></html>'
        mock_response = MagicMock()
        mock_response.read.return_value = mock_html.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        price1 = self.marketplace.get_crypto_price('BTC')
        self.assertEqual(price1, 45678.90)
        
        mock_urlopen.side_effect = Exception("Network error")
        
        price2 = self.marketplace.get_crypto_price('BTC')
        self.assertEqual(price2, 45678.90)
    
    # Test buy crypto
    @patch('urllib.request.urlopen')
    def test_buy_crypto_success(self, mock_urlopen):
        """Test successful crypto purchase."""
        mock_html = '<html><body>Price: $50,000.00</body></html>'
        mock_response = MagicMock()
        mock_response.read.return_value = mock_html.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        self.marketplace.deposit_fiat(self.test_username, 100000.0)
        
        result = self.marketplace.buy_crypto(self.test_username, 'BTC', 1.0)
        
        self.assertTrue(result)
        self.assertEqual(
            self.marketplace.users[self.test_username]['fiat_balance'], 
            50000.0
        )
        self.assertEqual(
            self.marketplace.users[self.test_username]['crypto_balances']['BTC'], 
            1.0
        )
    
    @patch('urllib.request.urlopen')
    def test_buy_crypto_insufficient_balance(self, mock_urlopen):
        """Test buy fails with insufficient balance."""
        mock_html = '<html><body>Price: $50,000.00</body></html>'
        mock_response = MagicMock()
        mock_response.read.return_value = mock_html.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        self.marketplace.deposit_fiat(self.test_username, 10000.0)
        
        result = self.marketplace.buy_crypto(self.test_username, 'BTC', 1.0)
        
        self.assertFalse(result)
    
    def test_buy_crypto_invalid_symbol(self):
        """Test buy fails with invalid symbol."""
        self.marketplace.register_user(
            self.test_username, 
            self.test_email, 
            self.test_password
        )
        self.marketplace.deposit_fiat(self.test_username, 10000.0)
        
        result = self.marketplace.buy_crypto(self.test_username, 'INVALID', 1.0)
        self.assertFalse(result)
    
    def test_buy_crypto_negative_quantity(self):
        """Test buy fails with negative quantity."""
        self.marketplace
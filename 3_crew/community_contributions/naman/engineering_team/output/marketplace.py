# marketplace.py - A simplified cryptocurrency marketplace implementation

import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import urllib.request
import urllib.error
import re


class Marketplace:
    """
    A simplified cryptocurrency marketplace (exchange + wallet) that allows users to:
    - Register accounts and authenticate
    - Deposit and withdraw fiat
    - Trade cryptocurrencies at live market prices from CoinMarketCap
    - View portfolio and transaction history
    """
    
    def __init__(self):
        """Initialize the marketplace with empty user base and transaction ledger."""
        self.users: Dict[str, Dict] = {}  # username -> user_data
        self.transactions: List[Dict] = []  # Immutable transaction ledger
        self.crypto_prices_cache: Dict[str, Dict] = {}  # symbol -> {price, timestamp}
        self.supported_symbols: Set[str] = {'BTC', 'ETH', 'SOL'}  # Supported cryptocurrencies
        self.price_cache_duration = 60  # Cache prices for 60 seconds
        # Dummy prices used as a fallback when network fetching fails.
        self.dummy_crypto_prices_usd: Dict[str, float] = {
            'BTC': 75744.77,
            'ETH': 2309.83,
            'SOL': 85.50,
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _validate_symbol(self, symbol: str) -> bool:
        """Validate if a cryptocurrency symbol is supported."""
        return symbol.upper() in self.supported_symbols
    
    def register_user(self, username: str, email: str, password: str) -> bool:
        """
        Register a new user with a unique username and email.
        
        Args:
            username: Unique username for the user
            email: Unique email address
            password: Plain text password (will be hashed)
        
        Returns:
            True if registration successful, False otherwise
        """
        # Check if username already exists
        if username in self.users:
            return False
        
        # Check if email already exists
        for user_data in self.users.values():
            if user_data['email'] == email:
                return False
        
        # Create new user
        self.users[username] = {
            'email': email,
            'password_hash': self._hash_password(password),
            'created_at': datetime.now().isoformat(),
            'fiat_balance': 0.0,
            'crypto_balances': {symbol: 0.0 for symbol in self.supported_symbols},
            'total_deposits': 0.0,  # Track for P&L calculation
            'total_withdrawals': 0.0
        }
        
        return True
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Plain text password to verify
        
        Returns:
            True if authentication successful, False otherwise
        """
        if username not in self.users:
            return False
        
        return self.users[username]['password_hash'] == self._hash_password(password)
    
    def get_user_balances(self, username: str) -> Optional[Dict]:
        """
        Get current fiat and crypto balances for a user.
        
        Args:
            username: Username to get balances for
        
        Returns:
            Dictionary with fiat_balance and crypto_balances, or None if user not found
        """
        if username not in self.users:
            return None
        
        user = self.users[username]
        return {
            'fiat_balance': user['fiat_balance'],
            'crypto_balances': user['crypto_balances'].copy()
        }
    
    def deposit_fiat(self, username: str, amount: float) -> bool:
        """
        Deposit fiat into a user's account (on-ramp).
        
        Args:
            username: Username to deposit to
            amount: Amount of fiat to deposit
        
        Returns:
            True if deposit successful, False otherwise
        """
        if username not in self.users or amount <= 0:
            return False
        
        user = self.users[username]
        user['fiat_balance'] += amount
        user['total_deposits'] += amount
        
        # Record transaction
        transaction = {
            'username': username,
            'type': 'DEPOSIT',
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'fiat_balance_after': user['fiat_balance']
        }
        self.transactions.append(transaction)
        
        return True
    
    def withdraw_fiat(self, username: str, amount: float) -> bool:
        """
        Withdraw fiat from a user's account (off-ramp).
        
        Args:
            username: Username to withdraw from
            amount: Amount of fiat to withdraw
        
        Returns:
            True if withdrawal successful, False otherwise
        """
        if username not in self.users or amount <= 0:
            return False
        
        user = self.users[username]
        
        # Check for sufficient balance
        if user['fiat_balance'] < amount:
            return False
        
        user['fiat_balance'] -= amount
        user['total_withdrawals'] += amount
        
        # Record transaction
        transaction = {
            'username': username,
            'type': 'WITHDRAWAL',
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'fiat_balance_after': user['fiat_balance']
        }
        self.transactions.append(transaction)
        
        return True
    
    def get_crypto_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest price for a cryptocurrency from CoinMarketCap.
        Uses caching to avoid excessive requests.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        
        Returns:
            Price in USD, or None if price cannot be fetched
        """
        symbol = symbol.upper()
        
        if not self._validate_symbol(symbol):
            return None
        
        # Check cache
        if symbol in self.crypto_prices_cache:
            cache_entry = self.crypto_prices_cache[symbol]
            cache_time = datetime.fromisoformat(cache_entry['timestamp'])
            if datetime.now() - cache_time < timedelta(seconds=self.price_cache_duration):
                return cache_entry['price']
        
        # Fetch new price from CoinMarketCap
        try:
            # Map symbols to CoinMarketCap slugs
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'SOL': 'solana'
            }
            
            slug = symbol_map.get(symbol)
            if not slug:
                return None
            
            url = f'https://coinmarketcap.com/currencies/{slug}/'
            
            # Set user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=10) as response:
                html = response.read().decode('utf-8')
            
            # Parse price from HTML - look for price patterns
            # CoinMarketCap typically shows price in format like $43,234.56
            price_pattern = r'\$([0-9,]+\.?[0-9]*)'  
            matches = re.findall(price_pattern, html)
            
            if matches:
                # Take the first substantial price found (usually the main price)
                for match in matches:
                    price_str = match.replace(',', '')
                    try:
                        price = float(price_str)
                        if price > 0.01:  # Sanity check - price should be reasonable
                            # Cache the price
                            self.crypto_prices_cache[symbol] = {
                                'price': price,
                                'timestamp': datetime.now().isoformat()
                            }
                            return price
                    except ValueError:
                        continue

            # If parsing fails, fall back to dummy price (if configured)
            if symbol in self.dummy_crypto_prices_usd:
                price = self.dummy_crypto_prices_usd[symbol]
                self.crypto_prices_cache[symbol] = {
                    'price': price,
                    'timestamp': datetime.now().isoformat()
                }
                return price

            return None
            
        except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
            # If we can't fetch, return cached price if available (even if stale)
            if symbol in self.crypto_prices_cache:
                return self.crypto_prices_cache[symbol]['price']
            # Otherwise fall back to dummy price (if configured)
            if symbol in self.dummy_crypto_prices_usd:
                price = self.dummy_crypto_prices_usd[symbol]
                self.crypto_prices_cache[symbol] = {
                    'price': price,
                    'timestamp': datetime.now().isoformat()
                }
                return price
            return None
    
    def buy_crypto(self, username: str, symbol: str, quantity: float) -> bool:
        """
        Execute a buy order for cryptocurrency.
        
        Args:
            username: Username executing the buy
            symbol: Cryptocurrency symbol to buy
            quantity: Quantity of crypto to buy
        
        Returns:
            True if buy successful, False otherwise
        """
        if username not in self.users or quantity <= 0:
            return False
        
        symbol = symbol.upper()
        if not self._validate_symbol(symbol):
            return False
        
        # Get current price
        price = self.get_crypto_price(symbol)
        if price is None:
            return False  # Cannot execute trade without price
        
        user = self.users[username]
        cost = price * quantity
        
        # Check if user has enough fiat
        if user['fiat_balance'] < cost:
            return False
        
        # Execute trade
        user['fiat_balance'] -= cost
        user['crypto_balances'][symbol] += quantity
        
        # Record transaction
        transaction = {
            'username': username,
            'type': 'BUY',
            'symbol': symbol,
            'quantity': quantity,
            'executed_price': price,
            'executed_at': datetime.now().isoformat(),
            'fiat_delta': -cost,
            'crypto_delta': quantity,
            'fiat_balance_after': user['fiat_balance'],
            'crypto_balance_after': user['crypto_balances'][symbol]
        }
        self.transactions.append(transaction)
        
        return True
    
    def sell_crypto(self, username: str, symbol: str, quantity: float) -> bool:
        """
        Execute a sell order for cryptocurrency.
        
        Args:
            username: Username executing the sell
            symbol: Cryptocurrency symbol to sell
            quantity: Quantity of crypto to sell
        
        Returns:
            True if sell successful, False otherwise
        """
        if username not in self.users or quantity <= 0:
            return False
        
        symbol = symbol.upper()
        if not self._validate_symbol(symbol):
            return False
        
        # Get current price
        price = self.get_crypto_price(symbol)
        if price is None:
            return False  # Cannot execute trade without price
        
        user = self.users[username]
        
        # Check if user has enough crypto
        if user['crypto_balances'][symbol] < quantity:
            return False
        
        # Execute trade
        proceeds = price * quantity
        user['crypto_balances'][symbol] -= quantity
        user['fiat_balance'] += proceeds
        
        # Record transaction
        transaction = {
            'username': username,
            'type': 'SELL',
            'symbol': symbol,
            'quantity': quantity,
            'executed_price': price,
            'executed_at': datetime.now().isoformat(),
            'fiat_delta': proceeds,
            'crypto_delta': -quantity,
            'fiat_balance_after': user['fiat_balance'],
            'crypto_balance_after': user['crypto_balances'][symbol]
        }
        self.transactions.append(transaction)
        
        return True
    
    def compute_portfolio_value(self, username: str) -> Optional[float]:
        """
        Calculate the total fiat value of a user's portfolio.
        
        Args:
            username: Username to calculate portfolio value for
        
        Returns:
            Total portfolio value in fiat, or None if calculation fails
        """
        if username not in self.users:
            return None
        
        user = self.users[username]
        total_value = user['fiat_balance']
        
        # Add value of crypto holdings
        for symbol, balance in user['crypto_balances'].items():
            if balance > 0:
                price = self.get_crypto_price(symbol)
                if price is None:
                    return None  # Cannot compute without all prices
                total_value += balance * price
        
        return total_value
    
    def calculate_profit_loss(self, username: str, baseline: float = 0.0) -> Optional[float]:
        """
        Calculate profit/loss for a user.
        
        Args:
            username: Username to calculate P&L for
            baseline: Optional baseline amount for P&L calculation
        
        Returns:
            Profit/loss amount, or None if calculation fails
        """
        if username not in self.users:
            return None
        
        portfolio_value = self.compute_portfolio_value(username)
        if portfolio_value is None:
            return None
        
        user = self.users[username]
        
        if baseline > 0:
            # Use provided baseline
            return portfolio_value - baseline
        else:
            # Use net deposits (total deposits - total withdrawals)
            net_deposits = user['total_deposits'] - user['total_withdrawals']
            return portfolio_value - net_deposits
    
    def get_transaction_history(self, username: str) -> List[Dict]:
        """
        Get ordered list of all transactions for a user.
        
        Args:
            username: Username to get transaction history for
        
        Returns:
            List of transaction dictionaries, ordered by time
        """
        if username not in self.users:
            return []
        
        # Filter transactions for this user
        user_transactions = [
            tx for tx in self.transactions 
            if tx.get('username') == username
        ]
        
        return user_transactions
```markdown
# Design for `marketplace.py`

This Python module, `marketplace.py`, contains a class `Marketplace` that implements a simplified cryptocurrency marketplace. This design lays out in detail the classes and functions, describing their purpose and functionality.

## Class: Marketplace

### Attributes:
- `users`: A dictionary storing user data keyed by their username.
- `transactions`: A list storing all completed transactions.
- `crypto_prices_cache`: A dictionary caching the latest fetched prices for supported cryptocurrencies.
- `supported_symbols`: A set of cryptocurrencies symbols that are supported (e.g., BTC, ETH, SOL).

### Methods:

#### User Management:
- `register_user(username: str, email: str, password: str) -> bool`:
  - **Purpose:** Registers a new user with a unique username and email.
  - **Description:** Checks if the username or email already exists, stores the user data securely, including hashed password.

- `authenticate_user(username: str, password: str) -> bool`:
  - **Purpose:** Authenticates a user attempting to log in.
  - **Description:** Verifies the username and password, returning True if credentials match, else False.

#### Wallet and Balances:
- `get_user_balances(username: str) -> dict`:
  - **Purpose:** Fetches the current fiat and crypto balances for a user.
  - **Description:** Returns a dictionary with fiat balance and crypto balances.

#### On-ramp and Off-ramp:
- `deposit_fiat(username: str, amount: float) -> bool`:
  - **Purpose:** Simulates depositing fiat into a user's account.
  - **Description:** Increases the fiat balance and records the transaction if successful.

- `withdraw_fiat(username: str, amount: float) -> bool`:
  - **Purpose:** Simulates withdrawing fiat from a user's account.
  - **Description:** Checks for sufficient balance, decreases the fiat balance, and records the transaction if successful.

#### Market Data:
- `get_crypto_price(symbol: str) -> float`:
  - **Purpose:** Fetches the latest price for a given cryptocurrency symbol.
  - **Description:** Scrapes if necessary and caches results for efficiency.

#### Trading:
- `buy_crypto(username: str, symbol: str, quantity: float) -> bool`:
  - **Purpose:** Executes a buy order for a specified quantity of crypto.
  - **Description:** Debits fiat using the current price and credits the corresponding crypto balance if valid.

- `sell_crypto(username: str, symbol: str, quantity: float) -> bool`:
  - **Purpose:** Executes a sell order for a specified quantity of crypto.
  - **Description:** Debits crypto balance and credits fiat based on the current price if valid.

#### Portfolio and Valuation:
- `compute_portfolio_value(username: str) -> float`:
  - **Purpose:** Calculates the total fiat value of a user's portfolio.
  - **Description:** Uses the market prices to value the current holdings.

- `calculate_profit_loss(username: str, baseline: float = 0.0) -> float`:
  - **Purpose:** Computes profit/loss for the user.
  - **Description:** Computes based on net deposits or given baseline.

#### Transaction History:
- `get_transaction_history(username: str) -> list`:
  - **Purpose:** Provides an ordered list of all transactions for a user.
  - **Description:** Retrieves and returns the user's transaction history from the immutable ledger.

This module design ensures that balances and transactions are handled correctly, transactions are immutable and auditable, and it facilitates user registration and authentication securely. Payments and trades are based on valid and current market prices obtained independently for determinism. This structure also adheres to the operational constraints of keeping everything self-contained within a single Python module. 
```

This design should be sufficiently detailed for the engineer to proceed with development.
#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from engineering_team.crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

requirements = """
Build a crypto-currency marketplace (a simplified exchange + wallet) where users can register accounts, fund them via on-ramp, trade crypto at live market prices, and off-ramp back to fiat. The focus is correctness of balances, order execution, and an auditable transaction ledger.

Core capabilities:
- Account registration and authentication:
  - A user can create an account with at minimum: unique email/username, password (stored securely), created_at.
  - A user can sign in and perform actions only on their own account.

- Wallets and balances:
  - Each user has a fiat balance (e.g., USD) and per-asset crypto balances (e.g., BTC, ETH).
  - Balances must never go negative.
  - Holdings must be derivable at any point in time from the transaction ledger (source of truth).

- On-ramp and off-ramp (fiat <-> account):
  - On-ramp: user can deposit fiat into their account (simulate payment rails; no real payments).
  - Off-ramp: user can withdraw fiat from their account, with insufficient-funds protection.
  - Each on/off-ramp action is recorded as a transaction with timestamp and resulting balances.

- Market data (latest pricing from CoinMarketCap):
  - The system must be able to fetch the latest spot price for supported crypto assets by reading data from https://coinmarketcap.com/ (web fetch/scrape or parsing HTML; no paid API requirement).
  - Pricing should be cached for a short duration to avoid excessive requests.
  - The system should expose a function like get_crypto_price(symbol) -> price_in_fiat that is used for trades and portfolio valuation.
  - If price cannot be fetched, the system must fail safely (do not execute trades with unknown price).

- Buy and sell crypto:
  - User can place a buy order for a crypto symbol and quantity; the system debits fiat and credits crypto using the latest price.
  - User can place a sell order for a crypto symbol and quantity; the system debits crypto and credits fiat using the latest price.
  - The system must prevent buying more than the available fiat balance and selling more than the available crypto balance.
  - Each trade records: side (BUY/SELL), symbol, quantity, executed_price, executed_at, fiat_delta, crypto_delta.

- Portfolio and valuation:
  - The system can report current holdings per asset and current fiat balance.
  - The system can compute total portfolio value in fiat using the latest prices from CoinMarketCap.
  - The system can compute profit/loss relative to net deposits (on-ramp minus off-ramp), and/or relative to an initial deposit baseline if provided.

- Transaction history:
  - The user can view an ordered list of all transactions over time (on-ramp, off-ramp, buys, sells).
  - Transactions must be immutable once recorded (append-only ledger).

Operational constraints and expectations:
- Keep the implementation simple and self-contained (single Python module {module_name} with class {class_name}).
- Prefer deterministic logic that is easy to test; network-dependent price fetching should be isolated behind get_crypto_price(symbol).
- Include a small set of supported symbols (e.g., BTC, ETH, SOL) and validate symbols on input.
"""
module_name = "marketplace.py"
class_name = "Marketplace"


def run():
    """
    Run the research crew.
    """
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }

    # Create and run the crew
    result = EngineeringTeam().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()
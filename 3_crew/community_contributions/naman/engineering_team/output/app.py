import gradio as gr
from marketplace import Marketplace
import pandas as pd

# Initialize marketplace and create a default user
marketplace = Marketplace()
DEFAULT_USER = "demo_user"
DEFAULT_EMAIL = "demo@example.com"
DEFAULT_PASSWORD = "demo123"

# Register default user
marketplace.register_user(DEFAULT_USER, DEFAULT_EMAIL, DEFAULT_PASSWORD)

def deposit_fiat(amount):
    try:
        amount = float(amount)
        if marketplace.deposit_fiat(DEFAULT_USER, amount):
            balances = marketplace.get_user_balances(DEFAULT_USER)
            return f"✅ Deposited ${amount:.2f}. New balance: ${balances['fiat_balance']:.2f}"
        return "❌ Deposit failed. Please check the amount."
    except ValueError:
        return "❌ Invalid amount. Please enter a number."

def withdraw_fiat(amount):
    try:
        amount = float(amount)
        if marketplace.withdraw_fiat(DEFAULT_USER, amount):
            balances = marketplace.get_user_balances(DEFAULT_USER)
            return f"✅ Withdrew ${amount:.2f}. New balance: ${balances['fiat_balance']:.2f}"
        return "❌ Withdrawal failed. Insufficient funds or invalid amount."
    except ValueError:
        return "❌ Invalid amount. Please enter a number."

def buy_crypto(symbol, quantity):
    try:
        quantity = float(quantity)
        symbol = symbol.upper()
        price = marketplace.get_crypto_price(symbol)
        if price is None:
            return f"❌ Could not fetch price for {symbol}. Please try again."
        
        cost = price * quantity
        if marketplace.buy_crypto(DEFAULT_USER, symbol, quantity):
            balances = marketplace.get_user_balances(DEFAULT_USER)
            return f"✅ Bought {quantity} {symbol} at ${price:.2f} each (total: ${cost:.2f})\nNew {symbol} balance: {balances['crypto_balances'][symbol]:.6f}\nFiat balance: ${balances['fiat_balance']:.2f}"
        return f"❌ Purchase failed. Insufficient funds (need ${cost:.2f}) or invalid input."
    except ValueError:
        return "❌ Invalid quantity. Please enter a number."

def sell_crypto(symbol, quantity):
    try:
        quantity = float(quantity)
        symbol = symbol.upper()
        price = marketplace.get_crypto_price(symbol)
        if price is None:
            return f"❌ Could not fetch price for {symbol}. Please try again."
        
        proceeds = price * quantity
        if marketplace.sell_crypto(DEFAULT_USER, symbol, quantity):
            balances = marketplace.get_user_balances(DEFAULT_USER)
            return f"✅ Sold {quantity} {symbol} at ${price:.2f} each (total: ${proceeds:.2f})\nNew {symbol} balance: {balances['crypto_balances'][symbol]:.6f}\nFiat balance: ${balances['fiat_balance']:.2f}"
        return f"❌ Sale failed. Insufficient {symbol} holdings or invalid input."
    except ValueError:
        return "❌ Invalid quantity. Please enter a number."

def get_balances():
    balances = marketplace.get_user_balances(DEFAULT_USER)
    if balances is None:
        return "❌ Error fetching balances"
    
    output = f"💵 Fiat Balance: ${balances['fiat_balance']:.2f}\n\n📊 Crypto Holdings:\n"
    for symbol, amount in balances['crypto_balances'].items():
        price = marketplace.get_crypto_price(symbol)
        if price and amount > 0:
            value = amount * price
            output += f"  {symbol}: {amount:.6f} (≈ ${value:.2f} @ ${price:.2f})\n"
        elif amount > 0:
            output += f"  {symbol}: {amount:.6f} (price unavailable)\n"
        else:
            output += f"  {symbol}: {amount:.6f}\n"
    
    return output

def get_portfolio_value():
    portfolio_value = marketplace.compute_portfolio_value(DEFAULT_USER)
    if portfolio_value is None:
        return "❌ Could not compute portfolio value (price data unavailable)"
    
    profit_loss = marketplace.calculate_profit_loss(DEFAULT_USER)
    pl_indicator = "📈" if profit_loss and profit_loss > 0 else "📉" if profit_loss and profit_loss < 0 else "➖"
    
    output = f"💼 Total Portfolio Value: ${portfolio_value:.2f}\n"
    if profit_loss is not None:
        output += f"{pl_indicator} Profit/Loss: ${profit_loss:.2f} ({(profit_loss/max(portfolio_value-profit_loss, 0.01))*100:.2f}%)"
    
    return output

def get_transaction_history():
    transactions = marketplace.get_transaction_history(DEFAULT_USER)
    if not transactions:
        return "No transactions yet."
    
    # Create DataFrame for better formatting
    tx_data = []
    for tx in transactions:
        ts = tx.get('timestamp') or tx.get('executed_at') or ""
        if tx['type'] in ['DEPOSIT', 'WITHDRAWAL']:
            tx_data.append({
                'Time': ts[:19] if ts else "-",
                'Type': tx['type'],
                'Symbol': '-',
                'Quantity': '-',
                'Price': '-',
                'Amount': f"${tx['amount']:.2f}",
                'Balance': f"${tx['fiat_balance_after']:.2f}"
            })
        else:  # BUY or SELL
            tx_data.append({
                'Time': ts[:19] if ts else "-",
                'Type': tx['type'],
                'Symbol': tx['symbol'],
                'Quantity': f"{tx['quantity']:.6f}",
                'Price': f"${tx['executed_price']:.2f}",
                'Amount': f"${abs(tx['fiat_delta']):.2f}",
                'Balance': f"${tx['fiat_balance_after']:.2f}"
            })
    
    df = pd.DataFrame(tx_data)
    return df

def get_current_prices():
    output = "💹 Current Market Prices:\n\n"
    for symbol in marketplace.supported_symbols:
        price = marketplace.get_crypto_price(symbol)
        if price:
            output += f"{symbol}: ${price:,.2f}\n"
        else:
            output += f"{symbol}: Price unavailable\n"
    return output

# Create Gradio interface with tabs
with gr.Blocks(title="Crypto Marketplace Demo", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🪙 Cryptocurrency Marketplace Demo")
    gr.Markdown(f"**Demo User:** {DEFAULT_USER} | **Supported Crypto:** BTC, ETH, SOL")
    
    with gr.Tabs():
        # Fiat Operations Tab
        with gr.Tab("💵 Fiat Operations"):
            gr.Markdown("### Deposit and Withdraw Fiat Currency")
            with gr.Row():
                with gr.Column():
                    deposit_amount = gr.Number(label="Deposit Amount ($)", value=1000)
                    deposit_btn = gr.Button("Deposit", variant="primary")
                    deposit_output = gr.Textbox(label="Result", lines=2)
                
                with gr.Column():
                    withdraw_amount = gr.Number(label="Withdrawal Amount ($)", value=100)
                    withdraw_btn = gr.Button("Withdraw", variant="secondary")
                    withdraw_output = gr.Textbox(label="Result", lines=2)
            
            deposit_btn.click(deposit_fiat, inputs=deposit_amount, outputs=deposit_output)
            withdraw_btn.click(withdraw_fiat, inputs=withdraw_amount, outputs=withdraw_output)
        
        # Trading Tab
        with gr.Tab("📈 Trade Crypto"):
            gr.Markdown("### Buy and Sell Cryptocurrency")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("**Buy Crypto**")
                    buy_symbol = gr.Dropdown(choices=["BTC", "ETH", "SOL"], label="Symbol", value="BTC")
                    buy_quantity = gr.Number(label="Quantity", value=0.001)
                    buy_btn = gr.Button("Buy", variant="primary")
                    buy_output = gr.Textbox(label="Result", lines=4)
                
                with gr.Column():
                    gr.Markdown("**Sell Crypto**")
                    sell_symbol = gr.Dropdown(choices=["BTC", "ETH", "SOL"], label="Symbol", value="BTC")
                    sell_quantity = gr.Number(label="Quantity", value=0.001)
                    sell_btn = gr.Button("Sell", variant="secondary")
                    sell_output = gr.Textbox(label="Result", lines=4)
            
            buy_btn.click(buy_crypto, inputs=[buy_symbol, buy_quantity], outputs=buy_output)
            sell_btn.click(sell_crypto, inputs=[sell_symbol, sell_quantity], outputs=sell_output)
        
        # Portfolio Tab
        with gr.Tab("💼 Portfolio"):
            gr.Markdown("### View Your Holdings and Portfolio Value")
            
            with gr.Row():
                refresh_balances_btn = gr.Button("Refresh Balances", variant="primary")
                refresh_portfolio_btn = gr.Button("Refresh Portfolio Value", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    balances_output = gr.Textbox(label="Current Balances", lines=10)
                with gr.Column():
                    portfolio_output = gr.Textbox(label="Portfolio Value & P/L", lines=10)
            
            refresh_balances_btn.click(get_balances, outputs=balances_output)
            refresh_portfolio_btn.click(get_portfolio_value, outputs=portfolio_output)
        
        # Transaction History Tab
        with gr.Tab("📜 Transaction History"):
            gr.Markdown("### View All Your Transactions")
            
            refresh_history_btn = gr.Button("Refresh Transaction History", variant="primary")
            history_output = gr.Dataframe(
                headers=["Time", "Type", "Symbol", "Quantity", "Price", "Amount", "Balance"],
                label="Transaction History",
                wrap=True
            )
            
            refresh_history_btn.click(get_transaction_history, outputs=history_output)
        
        # Market Prices Tab
        with gr.Tab("💹 Market Prices"):
            gr.Markdown("### Current Cryptocurrency Prices (from CoinMarketCap)")
            
            refresh_prices_btn = gr.Button("Refresh Prices", variant="primary")
            prices_output = gr.Textbox(label="Current Market Prices", lines=8)
            
            refresh_prices_btn.click(get_current_prices, outputs=prices_output)
    
    gr.Markdown("---")
    gr.Markdown("*Demo marketplace for educational purposes. Prices fetched from CoinMarketCap.*")

# Launch the app
if __name__ == "__main__":
    app.launch()

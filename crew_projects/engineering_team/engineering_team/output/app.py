from accounts import Account
import gradio as gr

account = Account(account_id="user123")

def deposit(amount):
    try:
        account.deposit(amount)
        return f"Deposited ${amount}. Current balance: ${account.balance}"
    except ValueError as e:
        return str(e)

def withdraw(amount):
    try:
        account.withdraw(amount)
        return f"Withdrew ${amount}. Current balance: ${account.balance}"
    except ValueError as e:
        return str(e)

def buy_shares(symbol, quantity):
    try:
        account.buy_shares(symbol, quantity)
        return f"Bought {quantity} shares of {symbol}. Current holdings: {account.get_holdings()}"
    except ValueError as e:
        return str(e)

def sell_shares(symbol, quantity):
    try:
        account.sell_shares(symbol, quantity)
        return f"Sold {quantity} shares of {symbol}. Current holdings: {account.get_holdings()}"
    except ValueError as e:
        return str(e)

def portfolio_value():
    return f"Total portfolio value: ${account.get_portfolio_value()}"

def profit_loss():
    return f"Profit/Loss: ${account.get_profit_loss()}"

def transactions():
    return account.get_transactions()

with gr.Blocks() as demo:
    gr.Markdown("# Trading Account Management")
    deposit_amount = gr.Number(label="Deposit Amount")
    deposit_btn = gr.Button("Deposit")
    deposit_output = gr.Textbox()
    
    withdraw_amount = gr.Number(label="Withdraw Amount")
    withdraw_btn = gr.Button("Withdraw")
    withdraw_output = gr.Textbox()
    
    stock_symbol = gr.Textbox(label="Stock Symbol (AAPL, TSLA, GOOGL)")
    buy_quantity = gr.Number(label="Quantity to Buy")
    buy_btn = gr.Button("Buy Shares")
    buy_output = gr.Textbox()
    
    sell_quantity = gr.Number(label="Quantity to Sell")
    sell_btn = gr.Button("Sell Shares")
    sell_output = gr.Textbox()
    
    value_btn = gr.Button("Check Portfolio Value")
    value_output = gr.Textbox()
    
    profit_loss_btn = gr.Button("Check Profit/Loss")
    profit_loss_output = gr.Textbox()
    
    transactions_btn = gr.Button("Get Transactions")
    transactions_output = gr.Textbox()
    
    deposit_btn.click(deposit, inputs=[deposit_amount], outputs=deposit_output)
    withdraw_btn.click(withdraw, inputs=[withdraw_amount], outputs=withdraw_output)
    buy_btn.click(buy_shares, inputs=[stock_symbol, buy_quantity], outputs=buy_output)
    sell_btn.click(sell_shares, inputs=[stock_symbol, sell_quantity], outputs=sell_output)
    value_btn.click(portfolio_value, outputs=value_output)
    profit_loss_btn.click(profit_loss, outputs=profit_loss_output)
    transactions_btn.click(transactions, outputs=transactions_output)

demo.launch()
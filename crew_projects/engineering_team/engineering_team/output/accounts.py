class Account:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.balance = 0.0
        self.holdings = {}
        self.transactions = []

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than 0.")
        self.balance += amount
        self.transactions.append({
            'type': 'deposit',
            'amount': amount,
            'timestamp': self.get_timestamp()
        })

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than 0.")
        if self.balance - amount < 0:
            raise ValueError("Insufficient funds for withdrawal.")
        self.balance -= amount
        self.transactions.append({
            'type': 'withdrawal',
            'amount': amount,
            'timestamp': self.get_timestamp()
        })

    def buy_shares(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        share_price = get_share_price(symbol)
        total_cost = share_price * quantity
        if self.balance < total_cost:
            raise ValueError("Insufficient funds to buy shares.")
        
        self.balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self.transactions.append({
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'amount': total_cost,
            'timestamp': self.get_timestamp()
        })

    def sell_shares(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            raise ValueError("Insufficient shares to sell.")
        
        share_price = get_share_price(symbol)
        total_income = share_price * quantity
        self.balance += total_income
        self.holdings[symbol] -= quantity
        
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]

        self.transactions.append({
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'amount': total_income,
            'timestamp': self.get_timestamp()
        })

    def get_portfolio_value(self) -> float:
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def get_profit_loss(self) -> float:
        total_invested = sum(txn['amount'] for txn in self.transactions if txn['type'] in ['deposit', 'buy'])
        return self.get_portfolio_value() - total_invested

    def get_holdings(self) -> dict:
        return self.holdings.copy()

    def get_transactions(self) -> list:
        return self.transactions.copy()

    def get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()


def get_share_price(symbol: str) -> float:
    prices = {
        'AAPL': 150.00,
        'TSLA': 700.00,
        'GOOGL': 2800.00
    }
    if symbol not in prices:
        raise ValueError("Unknown symbol.")
    return prices[symbol]
import unittest
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account('12345')

    def test_initial_balance(self):
        self.assertEqual(self.account.balance, 0.0)

    def test_deposit_success(self):
        self.account.deposit(100.0)
        self.assertEqual(self.account.balance, 100.0)

    def test_deposit_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-50.0)

    def test_withdraw_success(self):
        self.account.deposit(100.0)
        self.account.withdraw(50.0)
        self.assertEqual(self.account.balance, 50.0)

    def test_withdraw_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(50.0)

    def test_buy_shares_success(self):
        self.account.deposit(1000.0)
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.holdings['AAPL'], 2)
        self.assertEqual(self.account.balance, 700.0)

    def test_buy_shares_insufficient_funds(self):
        self.account.deposit(100.0)
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 2)

    def test_sell_shares_success(self):
        self.account.deposit(1000.0)
        self.account.buy_shares('AAPL', 2)
        self.account.sell_shares('AAPL', 1)
        self.assertEqual(self.account.holdings['AAPL'], 1)
        self.assertEqual(self.account.balance, 850.0)

    def test_sell_shares_insufficient_quantity(self):
        self.account.deposit(1000.0)
        self.account.buy_shares('AAPL', 1)
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 2)

    def test_get_portfolio_value(self):
        self.account.deposit(1000.0)
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.get_portfolio_value(), 850.0 + 300.0)

    def test_get_profit_loss(self):
        self.account.deposit(1000.0)
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.get_profit_loss(), 50.0)

    def test_get_holdings(self):
        self.account.deposit(1000.0)
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.get_holdings(), {'AAPL': 2})

    def test_get_transactions(self):
        self.account.deposit(1000.0)
        self.account.withdraw(200.0)
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)

if __name__ == '__main__':
    unittest.main()
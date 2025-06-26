from decimal import Decimal
from typing import Dict

class AccountManager:
    def __init__(self):
        self.balances: Dict[str, Dict[str, Decimal]] = {}

    def set_balance(self, user_id: str, currency: str, amount: Decimal):
        self.balances.setdefault(user_id, {})[currency] = amount

    def get_balance(self, user_id: str, currency: str) -> Decimal:
        return self.balances.get(user_id, {}).get(currency, Decimal("0"))

    def has_sufficient_funds(self, user_id: str, currency: str, required: Decimal) -> bool:
        return self.get_balance(user_id, currency) >= required

    def debit(self, user_id: str, currency: str, amount: Decimal):
        if not self.has_sufficient_funds(user_id, currency, amount):
            raise ValueError("Insufficient funds")
        self.balances[user_id][currency] -= amount

    def credit(self, user_id: str, currency: str, amount: Decimal):
        self.balances.setdefault(user_id, {})[currency] = self.get_balance(user_id, currency) + amount

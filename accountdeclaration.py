import collections
from dataclasses import dataclass
import unittest

from accountingsystemerror import AccountingSystemError
 
allowed_account_categories = {"Asset", "Liability", "Equity", "Revenue", "Expense"}

@dataclass(frozen=True)
class AccountDeclaration:
    category: str
    name: str

    def __post_init__(self):
        assert isinstance(self.category, str)
        assert isinstance(self.name, str)
        assert self.category in allowed_account_categories

    @classmethod
    def allowed_account_categories(cls):
        return allowed_account_categories


class Test(unittest.TestCase):
    def test_AccountDeclaration(self):
        x = AccountDeclaration(category='Asset', name='Cash')
        self.assertEqual(x.category, 'Asset')
        self.assertEqual(x.name, 'Cash')

if __name__ == "__main__":
    unittest.main()
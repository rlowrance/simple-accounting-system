import collections
import unittest

from accountingsystemerror import AccountingSystemError
 
Account = collections.namedtuple('Account', 'category name')

_allowed_account_categories = {"Asset", "Liability", "Equity", "Revenue", "Expense"}

def make(category_name = None, account_name = None) -> Account:
    category_name_capitalized = category_name.capitalize()
    if category_name_capitalized not in _allowed_account_categories:
        raise AccountingSystemError(f"invalid account category: {category_name}")
    if not isinstance(account_name, str):
        raise AccountingSystemError(f"account name not a string: found: {account_name}")
    account_name_splits = tuple(account_name.split())
    return Account(category_name_capitalized, account_name_splits)

class Test(unittest.TestCase):
    def test_make(self):
        account = make('aSSET', 'Accounts      Receivable')
        self.assertEqual(account.category, "Asset")
        self.assertEqual(account.name, ('Accounts', 'Receivable'))
        self.assertSequenceEqual(account.name, ("Accounts", "Receivable"))

if __name__ == "__main__":
    unittest.main()
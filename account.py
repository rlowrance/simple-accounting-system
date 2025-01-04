import collections
import unittest

from accountingsystemerror import AccountingSystemError
 
Account = collections.namedtuple('Account', 'category name')

_allowed_account_categories = {"Asset", "Liability", "Equity", "Revenue", "Expense"}

def make(category = None, name = None) -> Account:
    category_name_capitalized = category.capitalize()
    if category_name_capitalized not in _allowed_account_categories:
        raise AccountingSystemError(f"invalid account category: {category}")
    if not isinstance(name, str):
        raise AccountingSystemError(f"account name not a string: found: {name}")
    account_name_splits = tuple(name.split())
    return Account(category_name_capitalized, account_name_splits)

class Test(unittest.TestCase):
    def test_make(self):
        account = make('aSSET', 'Accounts      Receivable')
        self.assertEqual(account.category, "Asset")
        self.assertEqual(account.name, ('Accounts', 'Receivable'))
        self.assertSequenceEqual(account.name, ("Accounts", "Receivable"))

if __name__ == "__main__":
    unittest.main()
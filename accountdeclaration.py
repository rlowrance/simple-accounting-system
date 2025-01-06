import collections
import unittest

from accountingsystemerror import AccountingSystemError
 
AccountDeclaration = collections.namedtuple('AccountDeclaration', 'category name')

_allowed_account_categories = {"Asset", "Liability", "Equity", "Revenue", "Expense"}

def make(category = None, name = None) -> AccountDeclaration:
    if not isinstance(category, str):
        raise AccountingSystemError(f'account category {category} is not an instance of str')
    if category not in _allowed_account_categories:
        raise AccountingSystemError(f'invalid account category: {category} is not one of {_allowed_account_categories}')
    if not isinstance(name, str):
        raise AccountingSystemError(f'account name {name} is not an instance of str')
    return AccountDeclaration(category, name)

class Test(unittest.TestCase):
    def test_make(self):
        x = make(category='Asset', name='Cash')
        self.assertEqual(x.category, 'Asset')
        self.assertEqual(x.name, 'Cash')

if __name__ == "__main__":
    unittest.main()
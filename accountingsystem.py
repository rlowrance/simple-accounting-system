# Double-entry accounting with debits and credits
import collections
import unittest

import account
from accountingsystemerror import AccountingSystemError

AccountingSystem = collections.namedtuple('AccountingSystem', 'category_for ledgers balances last_journal_entry')
# We now have these methods
# as._make(iterable)
# as._asdict() -> Dict
# as._replace(**kwargs)
# as._fields : tuple of strings
# as._field_defaults: Dict

def empty_accounting_system(): return AccountingSystem({}, {}, {}, None)

def join_to_accounting_system(accounting_system, other) -> AccountingSystem:
    assert isinstance(accounting_system, AccountingSystem)
    if isinstance(other, account.Account):
        account_category = other.category
        account_name = other.name
        existing_category = accounting_system.category_for.get(account_name, None)
        if existing_category is None:
            accounting_system.category_for[account_name] = account_category
            return accounting_system._replace(category_for = accounting_system.category_for)
        else:
            if existing_category != account_category:
                raise AccountingSystemError(f'Attempt to redefine account category from {existing_category} to {account_category} for {account_name}')
            return accounting_system
    raise AccountingSystemError(f'internal error: join_to_accounting_system: type: {type(other)}\nother: {other}')

class TestJoinToAccountingSystem(unittest.TestCase):
    def test_empty_accounting_system(self):
        x = empty_accounting_system()
        self.assertEqual(x.category_for, {})
        self.assertEqual(x.ledgers, {})
        self.assertEqual(x.balances, {})
        self.assertEqual(x.last_journal_entry, None)

    def test_join_with_account(self):
        x0 = empty_accounting_system()
        x1 = join_to_accounting_system(x0, account.make('Asset', 'Cash'))
        key = ('Cash',)
        self.assertEqual(x1.category_for[key], 'Asset')
        self.assertEqual(x1.ledgers, {})
        x2 = join_to_accounting_system(x1, account.make('Asset', 'Cash'))
        self.assertAlmostEqual(x2.category_for[key], 'Asset')
        self.assertRaises(AccountingSystemError, join_to_accounting_system, x1, account.make('Liability', 'Cash'))


if __name__ == '__main__':
    unittest.main()
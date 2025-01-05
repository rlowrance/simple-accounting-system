# Double-entry accounting with debits and credits
import collections
import copy
import datetime
import unittest

import account as account_
import amount as amount_
from accountingsystemerror import AccountingSystemError
import entry as entry_
import journalentry as journalentry_
import posting as posting_

AccountingSystem = collections.namedtuple('AccountingSystem', 'category_for ledgers balances last_journal_entry')
# We now have these methods
# as._make(iterable)
# as._asdict() -> Dict
# as._replace(**kwargs)
# as._fields : tuple of strings
# as._field_defaults: Dict

def empty(): return AccountingSystem({}, {}, {}, None)

def make(category_for=None, ledgers=None, balances=None, last_journal_entry=None) -> AccountingSystem:
    def is_type(name, value, type):
        if not isinstance(value, type):
            raise AccountingSystemError(f'argument {name} with value {value} is not an instance of {type}')
    is_type('category_for', category_for, dict)
    is_type('ledgers', ledgers, dict)
    is_type('balances', balances, dict)
    is_type('last_journal_entry', last_journal_entry, journalentry_.JournalEntry)
    return AccountingSystem(category_for, ledgers, balances, last_journal_entry)

def _join_account(accounting_system, account) -> AccountingSystem:
    print('_join_account', accounting_system, account)
    existing_category = accounting_system.category_for.get(account.name, None)
    if existing_category is None:
        accounting_system.category_for[account.name] = account.category
        return accounting_system._replace(category_for=accounting_system.category_for)
    else:
        if existing_category != account.category:
            raise AccountingSystemError(f'attempt to redefine category for account {account.name} from {existing_category} to {account.category}')
        return accounting_system

def _join_journal_entry(accounting_system, journal_entry) -> AccountingSystem:
    def make_posting(side) -> posting_.Posting:
        return posting_.make(
            date=journal_entry.date,
            entry=entry_.make(
                side=side,
                amount=journal_entry.amount
            ),
            description=journal_entry.description,
            source=journal_entry.source,
            source_location=journal_entry.source_location
        )
    def make_zero_entry(side): return entry_.make(side=side, amount=amount_.make(dollars=0, cents=0))
    updated_ledgers = copy.copy(accounting_system.ledgers)
    if journal_entry.debit_account not in updated_ledgers:
        updated_ledgers[journal_entry.debit_account] = []
    if journal_entry.credit_account not in updated_ledgers:
        updated_ledgers[journal_entry.credit_account] = []
    updated_ledgers[journal_entry.debit_account].append(make_posting("debit"))
    updated_ledgers[journal_entry.credit_account].append(make_posting("credit"))

    updated_balances = copy.copy(accounting_system.balances)
    current_debit_balance = updated_balances.get(journal_entry.debit_account, make_zero_entry("debit"))
    updated_balances[journal_entry.debit_account] = entry_.add(current_debit_balance, entry_.make(side="debit", amount=journal_entry.amount))
    current_credit_balance = updated_balances.get(journal_entry.credit_account, make_zero_entry("credit"))
    updated_balances[journal_entry.credit_account] = entry_.add(current_credit_balance, entry_.make(side="credit", amount=journal_entry.amount))
    
    return make(
        category_for=accounting_system.category_for,
        ledgers=updated_ledgers,
        balances=updated_balances,
        last_journal_entry=copy.copy(journal_entry)
    )

def join(accounting_system, other) -> AccountingSystem:
    assert isinstance(accounting_system, AccountingSystem)
    if isinstance(other, account_.Account):
        return _join_account(accounting_system, other)
    if isinstance(other, journalentry_.JournalEntry):
        return _join_journal_entry(accounting_system, other)
    raise AccountingSystemError(f'internal error: join: type: {type(other)}\nother: {other}')

class TestJoinToAccountingSystem(unittest.TestCase):
    def test_join(self):
        cash = account_.make(category='asset', name='Cash')
        salaries = account_.make(category='expense', name='Salaries')
        postage = account_.make(category='expense', name='Postage')

        je1 = journalentry_.make(date=datetime.date.today(), 
                                amount=amount_.make(dollars=100, cents=1), 
                                debit_account=postage,
                                credit_account=cash,
                                description='buy postage',
                                source='file ffff.txt',
                                source_location='line 20')
        as1 = empty()
        as2 = join(as1, je1)
        self.assertEqual(3, len(as2.category_for))
        self.assertEqual(2, len(as2.ledgers))
        self.assertEqual(2, len(as2.balances))
        self.assertEqual(je1, as2.last_journal_entry)
        
        je2 = journalentry_.make(date=datetime.today(),
                                amount=amount_.make(dollars=200, cents=2),
                                debitAccount=salaries,
                                creditAccount=cash,
                                description='make payroll',
                                source='file gggg.csv',
                                source_location='line 21')
        as3 = join(as2, je2)
        self.assertEqual(3, len(as2.category_for))
        self.assertEqual(3, len(as2.ledgers))
        self.assertEqual(2, len(as2.balances))
        self.assertEqual(je2, as2.last_journal_entry)
        self.assertEqual(entry_.make(side='credit', amount=amount_.make(dollars=300, cents=3)), as2.balances[cash])

    def test_empty_accounting_system(self):
        x = empty()
        self.assertEqual(x.category_for, {})
        self.assertEqual(x.ledgers, {})
        self.assertEqual(x.balances, {})
        self.assertEqual(x.last_journal_entry, None)

    def test_join_with_account(self):
        x0 = empty()
        x1 = join(x0, account_.make('Asset', 'Cash'))
        key = ('Cash',)
        self.assertEqual(x1.category_for[key], 'Asset')
        self.assertEqual(x1.ledgers, {})
        x2 = join(x1, account_.make('Asset', 'Cash'))
        self.assertAlmostEqual(x2.category_for[key], 'Asset')
        self.assertRaises(AccountingSystemError, join, x1, account_.make('Liability', 'Cash'))


if __name__ == '__main__':
    unittest.main()
# Double-entry accounting with debits and credits
import collections
import copy
import datetime
import unittest

from pprint import pprint

import accountdeclaration as accountdeclaration_
import amount as amount_
from accountingsystemerror import AccountingSystemError
import journalentry as journalentry_
import ledgerentry as ledgerentry_
import line as line_

# ref: https://stackoverflow.com/questions/6330071/safe-casting-in-python
def safe_cast(value, to_type, default_value=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default_value

# ref: https://stackoverflow.com/questions/4071396/how-to-split-by-comma-and-strip-white-spaces-in-python
def split_and_strip(s, splitter=None) -> list:
    if splitter is None:
        return list(map(str.strip, s.split()))
    return list(map(str.strip, s.split(splitter)))

AccountingSystem = collections.namedtuple('AccountingSystem', 'category_for ledgers balances last_journal_entry')
# We now have these methods
# as._make(iterable)
# as._asdict() -> Dict
# as._replace(**kwargs)
# as._fields : tuple of strings
# as._field_defaults: Dict

def __str__(self) -> str:
    r = []
    r.append('AccountingSystem')
    r.append('  category_for')
    for k, v in self.category_for.items():
        r.append(f'    {k}: {v}')
    r.append('  ledgers')
    for k, v in self.ledgers.items():
        r.append(f'    {k}: {v}')
    r.append('  balances')
    for k, v in self.balances.items():
        r.append(f'    {k}: {v}')
    r.append('  last_journal_entry: {self.last_journal_entry}')
    return "\n".join(r)
AccountingSystem.__str__ = __str__

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

allowed_categories = {'Asset', 'Liability', 'Equity', 'Revenue', 'Expense'}

def _join_account_declaration(accounting_system, xs) -> AccountingSystem:
    if len(xs) != 2:
        raise AccountingSystemError(f'account declaration {xs} was not of length 2')
    category, name = xs
    if not isinstance(category, str):
        raise AccountingSystemError(f'account category {category} is not an instance of str')
    if not category in allowed_categories:
        raise AccountingSystemError(f'category {category} is not in allowed categories, which are {allowed_categories}')
    if not isinstance(name, str):
        raise AccountingSystemError(f'account name {name} is not an instance of str')
    existing_category = accounting_system.category_for.get(name, None)
    if existing_category is None:
        accounting_system.category_for[name] = category
        return accounting_system._replace(category_for=accounting_system.category_for)
    else:
        if existing_category != category:
            raise AccountingSystemError(f'attempt to redefine category for account {name} from {existing_category} to {category}')
        return accounting_system

def _join_journal_entry(accounting_system, journal_entry) -> AccountingSystem:
    assert isinstance(journal_entry, journalentry_.JournalEntry)
    def category_is_defined(account):
        category = accounting_system.category_for.get(account, None)
        if category is None:
            raise AccountingSystemError(f'account {account} has no defined category')
    def make_ledger_entry(side) -> ledgerentry_.LedgerEntry:
        return ledgerentry_.make(
            date=journal_entry.date,
            side=side,
            amount=journal_entry.amount,
            description=journal_entry.description,
            source=journal_entry.source,
            source_location=journal_entry.source_location
        )
    def make_zero_ledger_entry(side) -> ledgerentry_.LedgerEntry:
        return ledgerentry_.make(
            date=journal_entry.date,
            side=side,
            amount=amount_.make(dollars=0, cents=0),
            description=journal_entry.description,
            source=journal_entry.source,
            source_location=journal_entry.source_location
        )
    
    category_is_defined(journal_entry.debit_account)
    category_is_defined(journal_entry.credit_account)

    updated_ledgers = copy.copy(accounting_system.ledgers)
    if journal_entry.debit_account not in updated_ledgers:
        updated_ledgers[journal_entry.debit_account] = []
    if journal_entry.credit_account not in updated_ledgers:
        updated_ledgers[journal_entry.credit_account] = []
    updated_ledgers[journal_entry.debit_account].append(make_ledger_entry("debit"))
    updated_ledgers[journal_entry.credit_account].append(make_ledger_entry("credit"))

    updated_balances = copy.copy(accounting_system.balances)
    current_debit_balance = updated_balances.get(journal_entry.debit_account, make_zero_ledger_entry("debit"))
    updated_balances[journal_entry.debit_account] = ledgerentry_.add(current_debit_balance, 
                                                                     make_ledger_entry("debit"))
    current_credit_balance = updated_balances.get(journal_entry.credit_account, make_zero_ledger_entry("credit"))
    updated_balances[journal_entry.credit_account] = ledgerentry_.add(current_credit_balance,
                                                                      make_ledger_entry("credit"))
    
    return make(
        category_for=accounting_system.category_for,
        ledgers=updated_ledgers,
        balances=updated_balances,
        last_journal_entry=copy.copy(journal_entry)
    )

def _make_date(s, je) -> datetime.date:
    if len(s) == 8:
        return datetime.date.fromisoformat(s)
    if len(s) == 4:
        return _make_date(f'{je.date.year}{s}', je)
    if len(s) == 2:
        return _make_date(f'{je.date.year}{str(je.date.month).zfill(2)}{s}', je)
    raise AccountingSystemError('date not in format YYYYMMDD or MMDD or DD')


def _make_amount(s, je) -> amount_.Amount:
    splits = split_and_strip(s, ".")
    if len(splits) == 0:
        return je.amount
    if len(splits) == 2: # ex: 123.45
        a, b = splits
        dollars = safe_cast(a, int)
        cents = safe_cast(b, int)
        if dollars is None:
            raise AccountingSystemError(f'dollars amount {a} is not an int')
        if cents is None:
            raise AccountingSystemError(f'cents amount {b} is not an int')
        return amount_.make(dollars=dollars, cents=cents)
    raise AccountingSystemError(f's {s} is not like 123.45 (specifying dollars and cents)')

def _join_str(accounting_system, line) -> AccountingSystem:
    assert isinstance(line, line_.Line)
    text = line.text
    splits = split_and_strip(text, ',')
    if len(splits) == 1:
        items = split_and_strip(text, ':')
        if len(items) != 2:
            raise AccountingSystemError(f'account declaration {text} is not like Asset:Cash')
        return join(accounting_system, accountdeclaration_.make(category=items[0], name=items[1]))
    if len(splits) == 5:
        lje = accounting_system.last_journal_entry
        date, amount, credit_account, debit_account, description = splits
        je = journalentry_.make(
            date = _make_date(date, lje),
            amount = _make_amount(amount, lje),
            debit_account=debit_account if len(debit_account) > 0 else lje.debit_account,
            credit_account=credit_account if len(credit_account) > 0 else lje.credit_account,
            description=description,
            source=line.source,
            source_location=line.source_location
        )
        return join(accounting_system, je)
    if len(splits) == 2:
        lje = accounting_system.last_journal_entry
        date, amount = splits # name the strings
        je = journalentry_.make(
            date = _make_date(date, lje),
            amount = _make_amount(amount, lje),
            debit_account=lje.debit_account,
            credit_account=lje.credit_account,
            description=lje.description,
            source=line.source,
            source_location=line.source_location
        )
        return join(accounting_system, je)

def join(accounting_system, other) -> AccountingSystem:
    assert isinstance(accounting_system, AccountingSystem)
    if isinstance(other, line_.Line):
        return _join_str(accounting_system, other)
    if isinstance(other, accountdeclaration_.AccountDeclaration):
        return _join_account_declaration(accounting_system, other)
    if isinstance(other, journalentry_.JournalEntry):
        return _join_journal_entry(accounting_system, other)
    raise AccountingSystemError(f'internal error: join: type: {type(other)}\nother: {other}')

class Test(unittest.TestCase):
    def test_join_str(self):
        tests = (
            'Asset : cash',
            'Equity:owners equity',
            '20250106, 123.45, cash, owners equity, fund business',
            '07, 1.01', # additional funding
        )
        accounting_system = empty()
        line_number = 0
        for test in tests:
            line_number += 1
            accounting_system = join(
                accounting_system,
                line_.make(text=test, source="test case", source_location=f'line {line_number}'))
        self.assertEqual(accounting_system.balances['cash'].amount, amount_.make(dollars=124, cents=46))
        

    def test_join_journal_entry(self):
        as0 = empty()
        as0a = join(as0, accountdeclaration_.make(category='Asset', name='cash'))
        as0b = join(as0a, accountdeclaration_.make(category='Expense', name='salaries'))
        as0c = join(as0b, accountdeclaration_.make(category='Expense', name='postage'))
        self.assertEqual(3, len(as0c.category_for))

        je1 = journalentry_.make(date=datetime.date.today(), 
                                amount=amount_.make(dollars=100, cents=1), 
                                debit_account='postage',
                                credit_account='cash',
                                description='buy postage',
                                source='file ffff.txt',
                                source_location='line 20')
        as1 = as0c
        as2 = join(as1, je1)
        self.assertEqual(3, len(as2.category_for))
        self.assertEqual(2, len(as2.ledgers))
        self.assertEqual(2, len(as2.balances))
        self.assertEqual(je1, as2.last_journal_entry)

        je2 = journalentry_.make(date=datetime.date.today(),
                                amount=amount_.make(dollars=200, cents=2),
                                debit_account='salaries',
                                credit_account='cash',
                                description='make payroll',
                                source='file gggg.csv',
                                source_location='line 21')
        as3 = join(as2, je2)
        self.assertEqual(3, len(as3.category_for))
        self.assertEqual(3, len(as3.ledgers))
        self.assertEqual(3, len(as3.balances))
        self.assertEqual(je2, as3.last_journal_entry)
        self.assertEqual(as3.balances['cash'].side, 'credit')
        self.assertEqual(as3.balances['cash'].amount, amount_.make(dollars=300, cents=3))

    def test_empty_accounting_system(self):
        x = empty()
        self.assertEqual(x.category_for, {})
        self.assertEqual(x.ledgers, {})
        self.assertEqual(x.balances, {})
        self.assertEqual(x.last_journal_entry, None)

    def test_join_account_declaration(self):
        x0 = empty()
        ad = accountdeclaration_.make(category='Asset', name='Cash')
        x1 = join(x0, ad)
        self.assertEqual(x1.category_for['Cash'], 'Asset')
        self.assertEqual(x1.ledgers, {})
        x2 = join(x1, ad) # ignore redundant account declarations
        self.assertEqual(x2.category_for['Cash'], 'Asset')
        self.assertRaises(AccountingSystemError, join, x1, ('Liability', 'Cash'))


if __name__ == '__main__':
    unittest.main()
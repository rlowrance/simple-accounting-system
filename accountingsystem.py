# Double-entry accounting with debits and credits
import collections
from dataclasses import dataclass
import dataclasses
import copy
import datetime
from typing import Self, Union
import unittest

from pprint import pprint

from accountdeclaration import AccountDeclaration
from amount import Amount
from accountingsystemerror import AccountingSystemError
from journalentry import JournalEntry
from ledgerentry import LedgerEntry
from line import Line

@dataclass(frozen=True)
class AccountingSystem:
    category_for: dict
    ledgers: dict
    balances: dict
    last_journal_entry: Union[JournalEntry, None]

    def __post_init__(self):
        assert isinstance(self.category_for, dict)
        assert isinstance(self.ledgers, dict)
        assert isinstance(self.balances, dict)
        assert self.last_journal_entry is None or isinstance(self.last_journal_entry, JournalEntry)

    @classmethod
    def empty(cls) -> Self:
        return AccountingSystem(category_for={}, ledgers={}, balances={}, last_journal_entry=None)

    def render(self) -> tuple[str]:
        r = []
        r.append('AccountingSystem')
        def show(name, value):
            r.append(f'  {name}')
            for k, v in value.items():
                r.append(f'    {k}: {v}')
        show('category_for', self.category_for)
        show('ledgers', self.ledgers)
        show('balances', self.balances)
        r.append(f'  last_journal_entry: {self.last_journal_entry}')
        return tuple(r)

    def join(self, other) -> Self:
        if isinstance(other, AccountDeclaration): return self._join_account_declaration(other)
        if isinstance(other, JournalEntry): return self._join_journal_entry(other)
        assert False, f'attempt to join a {type(other)}'

    def _join_account_declaration(self, ad: AccountDeclaration) -> Self:
        existing_category = self.category_for.get(ad.name, None)
        if existing_category is None:
            new_category_for = copy.deepcopy(self.category_for)
            new_category_for[ad.name] = ad.category
            return dataclasses.replace(self, category_for=new_category_for)
        else:
            assert existing_category == ad.category
            return self

    def _join_journal_entry(self, je: JournalEntry) -> Self:
        debit_ledger_entry = LedgerEntry(
                date=je.date,
                side='debit',
                amount=je.amount,
                description=je.description,
                source=je.source,
                source_location=je.source_location
            )
        credit_ledger_entry = LedgerEntry(
                date=je.date,
                side='credit',
                amount=je.amount,
                description=je.description,
                source=je.source,
                source_location=je.source_location)
        def make_new_ledgers():  # the dict values are lists of ledger entries
            new_ledgers = copy.deepcopy(self.ledgers)
            if je.debit_account not in new_ledgers:
                new_ledgers[je.debit_account] = []
            if je.credit_account not in new_ledgers:
                new_ledgers[je.credit_account] = []
            new_ledgers[je.debit_account].append(debit_ledger_entry)
            new_ledgers[je.credit_account].append(credit_ledger_entry)
            return new_ledgers
        def make_new_balances():  # the dict values are a single ledger entry
            new_balances = copy.deepcopy(self.balances)
            new_balances[je.debit_account] = self.balances[je.debit_account].add(debit_ledger_entry) if je.debit_account in new_balances else debit_ledger_entry
            new_balances[je.credit_account] = self.balances[je.credit_account].add(credit_ledger_entry) if je.credit_account in new_balances else credit_ledger_entry
            return new_balances
        return dataclasses.replace(
            self,
            ledgers=make_new_ledgers(),
            balances=make_new_balances(),
            last_journal_entry=je
        )

class Test(unittest.TestCase):
    def test_join(self):
        account_declarations = (
            AccountDeclaration(category='Asset', name='cash'),
            AccountDeclaration(category='Asset', name='supplies'),
            AccountDeclaration(category='Equity', name='owners equity'),
        )
        x = AccountingSystem.empty()
        for account_declaration in account_declarations:
            x = x.join(account_declaration)
        def je(dollars, debit_account, credit_account):
            return JournalEntry(
                date=datetime.date.today(),
                amount=Amount(dollars=dollars, cents=0),
                debit_account = debit_account,
                credit_account=credit_account,
                description='',
                source='',
                source_location=''
            )
        tests = (
            (je(100, 'cash', 'owners equity'), 100),
            (je(10, 'supplies', 'cash'), 90)
        )
        for test in tests:
            journal_entry, expected_cash_balance = test
            print(journal_entry)
            x = x.join(journal_entry)
            self.assertEqual(expected_cash_balance, x.balances['cash'].amount.dollars)
        for line in x.render():
            print(line)

if __name__ == '__main__':
    unittest.main()
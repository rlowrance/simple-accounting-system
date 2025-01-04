import collections
import datetime
import unittest

import account
import amount

from accountingsystemerror import AccountingSystemError

JournalEntry = collections.namedtuple('JournalEntry', 'date amount debitAccount creditAccount description')

def make(date = None, amount = None, debitAccount = None, creditAccount = None, description = "") -> JournalEntry:
    if date is None:
        raise AccountingSystemError(f'missing argument date')
    if not isinstance(date, datetime.date):
        raise AccountingSystemError(f'date {date} is not a datetime.date')
    if amount is None:
        raise AccountingSystemError(f'missing argument amount')
    if not isinstance(amount, amount.Amount):
        raise AccountingSystemError(f'amount {amount} is not an Amount')
    if debitAccount is None:
        raise AccountingSystemError(f'missing argument debitAccount')
    if not isinstance(debitAccount, account.Account):
        raise AccountingSystemError(f'debitAccount {debitAccount} is not an Account')
    if creditAccount is None:
        raise AccountingSystemError(f'missing argument creditAccount')
    if not isinstance(creditAccount, account.Acount):
        raise AccountingSystemError(f'creditAccount {creditAccount} is not an Account')
    if not isinstance(description, str):
        raise AccountingSystemError(f'description {description} is not a str')
    return JournalEntry(date, amount, debitAccount, creditAccount, description)


class Test(unittest.TestCase):
    def test_make_ok(self):
        tests = (None, 'my description')
        for test in tests:
            the_date = datetime.date(1,1,1)
            the_amount = amount.Amount(100, 23)
            the_debit_account = account.make('Asset', 'cash')
            the_credit_account = account.make('Liability', 'loan')
            x = make(the_date, the_amount, the_debit_account, the_credit_account, test)
            self.assertTrue(isinstance(x, JournalEntry))

    
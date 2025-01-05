import collections
import datetime
import unittest

from account import Account
from account import make as account_make
from amount import Amount
from amount import make as amount_make

from accountingsystemerror import AccountingSystemError

JournalEntry = collections.namedtuple('JournalEntry', 'date amount debit_account credit_account description source source_location')

def make(date = None, amount = None, debit_account = None, credit_account = None, description = "", source=None, source_location=None) -> JournalEntry:
    def is_type(name, value, type):
        if not isinstance(value, type):
            raise AccountingSystemError(f'argument {name} with value {value} is not an instance of {type}')
    is_type('date', date, datetime.date)
    is_type('amount', amount, Amount)
    is_type('debitAccount', debit_account, Account)
    is_type('creditAccount', credit_account, Account)
    is_type('description', description, str)
    is_type('source', source, str)
    is_type('source_location', source_location, str)
    return JournalEntry(date, amount, debit_account, credit_account, description, source, source_location)


class Test(unittest.TestCase):
    def test_make_ok(self):
        tests = (None, 'my description')
        for test in tests:
            the_date = datetime.date(1,1,1)
            the_amount = Amount(100, 23)
            the_debit_account = account_make('Asset', 'cash')
            the_credit_account = account_make('Liability', 'loan')
            x = make(
                date=the_date,
                amount=the_amount,
                debit_account=the_debit_account,
                credit_account=the_credit_account,
                description="what happened",
                source="source.txt",
                source_location="line 0"
            )
            self.assertTrue(isinstance(x, JournalEntry))

if __name__ == '__main__':
    unittest.main()
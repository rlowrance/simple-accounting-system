import collections
import datetime
import unittest

#from account import Account
#from account import make as account_make
import amount as amount_

from accountingsystemerror import AccountingSystemError

JournalEntry = collections.namedtuple('JournalEntry', 'date amount debit_account credit_account description source source_location')

def make(date = None, amount = None, debit_account = None, credit_account = None, description = "", source=None, source_location=None) -> JournalEntry:
    def is_type(name, value, type):
        if not isinstance(value, type):
            raise AccountingSystemError(f'argument {name} with value {value} is not an instance of {type}')
    is_type('date', date, datetime.date)
    is_type('amount', amount, amount_.Amount)
    is_type('debitAccount', debit_account, str)
    is_type('creditAccount', credit_account, str)
    is_type('description', description, str)
    is_type('source', source, str)
    is_type('source_location', source_location, str)
    return JournalEntry(date, amount, debit_account, credit_account, description, source, source_location)


class Test(unittest.TestCase):
    def test_make_ok(self):
        tests = (None, 'my description')
        for test in tests:
            x = make(
                date=datetime.date(1,1,1),
                amount=amount_.make(dollars=100, cents=23),
                debit_account='Cash',
                credit_account='Loan',
                description="what happened",
                source="source.txt",
                source_location="line 0"
            )
            self.assertTrue(isinstance(x, JournalEntry))

if __name__ == '__main__':
    unittest.main()
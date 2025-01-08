import collections
from dataclasses import dataclass
import datetime
import unittest

#from account import Account
#from account import make as account_make
from amount import Amount

@dataclass
class JournalEntry:
    date: datetime.date
    amount: Amount
    debit_account: str
    credit_account: str
    description: str
    source: str
    source_location: str

    def __post_init__(self):
        assert isinstance(self.date, datetime.date)
        assert isinstance(self.amount, Amount)
        assert isinstance(self.debit_account, str)
        assert isinstance(self.credit_account, str)
        assert isinstance(self.description, str)
        assert isinstance(self.source, str)
        assert isinstance(self.source_location, str)


class Test(unittest.TestCase):
    def test_make_ok(self):
        tests = (None, 'my description')
        for test in tests:
            x = JournalEntry(
                date=datetime.date(1,1,1),
                amount=Amount(dollars=100, cents=23),
                debit_account='Cash',
                credit_account='Loan',
                description="what happened",
                source="source.txt",
                source_location="line 0"
            )
            self.assertTrue(isinstance(x, JournalEntry))

if __name__ == '__main__':
    unittest.main()
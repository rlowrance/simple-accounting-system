import collections
import dataclasses
from dataclasses import dataclass
import datetime
import unittest

from accountingsystemerror import AccountingSystemError
from amount import Amount
from balance import Balance

@dataclass
class LedgerEntry:
    date: datetime.date
    balance: Balance
    description: str
    source: str
    source_location: str

    def __post_init__(self):
        assert isinstance(self.date, datetime.date)
        assert isinstance(self.balance, Balance)
        assert isinstance(self.description, str)
        assert isinstance(self.source, str)
        assert isinstance(self.source_location, str)

class Test(unittest.TestCase):
    def test_construction(self):
        tests = (
            (datetime.date.today(), Balance(side='debit', amount=Amount(dollars=1, cents=23)), 'description', 'source', 'source_location'),
        )
        for test in tests:
            a, b, c, d, e = test
            r = LedgerEntry(date=a, balance=b, description=c, source=d, source_location=e)
            self.assertTrue(isinstance(r, LedgerEntry))


if __name__ == '__main__':
    unittest.main()
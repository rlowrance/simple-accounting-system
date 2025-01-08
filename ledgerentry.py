import collections
import dataclasses
from dataclasses import dataclass
import datetime
import unittest

from accountingsystemerror import AccountingSystemError
from amount import Amount

@dataclass
class LedgerEntry:
    date: datetime.date
    side: str
    amount: Amount
    description: str
    source: str
    source_location: str

    def __post_init__(self):
        assert isinstance(self.date, datetime.date)
        assert isinstance(self.side, str)
        assert isinstance(self.amount, Amount)
        assert isinstance(self.description, str)
        assert isinstance(self.source, str)
        assert isinstance(self.source_location, str)

    def add(self, other: 'LedgerEntry') -> 'LedgerEntry':
        assert isinstance(other, LedgerEntry)
        def make(side, amount: Amount) -> 'LedgerEntry':
            return dataclasses.replace(self, side=side, amount=amount)
        if self.side == other.side: return make(self.side, self.amount.add(other.amount))
        if self.amount.greater(other.amount): return make(self.side, self.amount.subtract(other.amount))
        if other.amount.greater(self.amount): return make(other.side, other.amount.subtract(self.amount))
        return make(self.side, Amount(dollars=0, cents=0))

class Test(unittest.TestCase):
    def test_add(self):
        tests = (
            (("debit", 100, 10), ("debit", 1, 2), ("debit", 101, 12)),
            (("debit", 100, 10), ("credit", 1, 2), ("debit", 99, 8)),
            (("debit", 100, 10), ("credit", 101, 12), ("credit", 1, 2)),
            (("credit", 100, 10), ("credit", 1, 2), ("credit", 101, 12)),
            (("credit", 100, 10), ("debit", 1, 2), ("credit", 99, 8)),
            (("credit", 100, 10), ("debit", 101, 12), ("debit", 1, 2)),
        )
        for test in tests:
            a, b, c = test
            def _make(x): return LedgerEntry(date=datetime.date.today(),
                                             side=x[0],
                                             amount=Amount(dollars=x[1], cents=x[2]),
                                             description="description",
                                             source="source",
                                             source_location="line 0"
            )
            x = _make(a)
            y = _make(b)
            expected = _make(c)
            actual = x.add(y)
            self.assertEqual(expected.side, actual.side)
            self.assertEqual(expected.amount, actual.amount)


if __name__ == '__main__':
    unittest.main()
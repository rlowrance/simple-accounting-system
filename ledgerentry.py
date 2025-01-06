import collections
import datetime
import unittest

from accountingsystemerror import AccountingSystemError
import amount as amount_

LedgerEntry = collections.namedtuple('LedgerEntry', 'date side amount description source source_location')

allowed_sides = {"debit", "credit"}

def make(date=None, side=None, amount=None, description=None, source=None, source_location=None) -> LedgerEntry:
    def is_type(name, value, type):
        if not isinstance(value, type):
            raise AccountingSystemError(f'argument {name} with value {value} is not an instance of type {type}')
    is_type('date', date, datetime.date)
    is_type('side', side, str)
    is_type('amount', amount, amount_.Amount)
    is_type('description', description, str)
    is_type('source', source, str)
    is_type('source_location', source_location, str)
    if side not in allowed_sides:
        raise AccountingSystemError(f'argument side with value {side} not in {allowed_sides}')
    return LedgerEntry(date, side, amount, description, source, source_location)

def add(lhs, rhs) -> LedgerEntry:
    assert isinstance(lhs, LedgerEntry)
    assert isinstance(rhs, LedgerEntry)
    def _make(side, amount):
        return make(
            date=max(lhs.date, rhs.date),
            side=side,
            amount=amount,
            description="add(LedgerEntry, LedgerEntry)",
            source="program",
            source_location="file ledgerentry.py"
        )
    if lhs.side == rhs.side:
        return _make(lhs.side, amount_.add(lhs.amount, rhs.amount))
    if amount_.greater(lhs.amount, rhs.amount):
        return _make(lhs.side, amount_.subtract(lhs.amount, rhs.amount))
    if amount_.greater(rhs.amount, lhs.amount):
        return _make(rhs.side, amount_.subtract(rhs.amount, lhs.amount))


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
                                             amount=amount_.make(dollars=x[1], cents=x[2]),
                                             description="description",
                                             source="source",
                                             source_location="line 0"
            )
            x = _make(a)
            y = _make(b)
            expected = _make(c)
            actual = add(x, y)
            self.assertEqual(expected.side, actual.side)
            self.assertEqual(expected.amount, actual.amount)




    def test_make(self):
        x = make(date=datetime.date(1,1,1), 
                 side="debit",
                 amount=amount_.make(dollars=100, cents=10),
                 description="something",
                 source="source",
                 source_location="location")
        self.assertTrue(True)  # just test run to completion

if __name__ == '__main__':
    unittest.main()
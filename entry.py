import collections
import unittest

from accountingsystemerror import AccountingSystemError
import amount as _amount

Entry = collections.namedtuple('Entry', 'side amount')

allowed_sides = {"debit", "credit"}

def make(side = None, amount = None) -> Entry:
    if side is None:
        raise AccountingSystemError(f'missing argument side')
    if side not in allowed_sides:
        raise AccountingSystemError(f'side {side} not in {allowed_sides}')
    if amount is None:
        raise AccountingSystemError(f'missing amount')
    if not isinstance(amount, _amount.Amount):
        raise AccountingSystemError(f'amount {amount} is not an Amount')
    return Entry(side, amount)

def add(lhs, rhs) -> Entry:
    assert isinstance(lhs, Entry)
    assert isinstance(rhs, Entry)
    if lhs.side == rhs.side:
        return Entry(lhs.side, _amount.add(lhs.amount, rhs.amount))
    if _amount.greater(lhs.amount, rhs.amount):
        return Entry(lhs.side, _amount.subtract(lhs.amount, rhs.amount))
    if _amount.greater(rhs.amount, lhs.amount):
        return Entry(rhs.side, _amount.subtract(rhs.amount, lhs.amount))
    return Entry(lhs.side, _amount.add(lhs.amount, rhs.amount))

class Test(unittest.TestCase):
    def test_make(self):
        tests = (
            ("debit", 100, 10, Entry("debit", _amount.make(100,10))),
            ("credit", 1, 23, Entry("credit", _amount.make(1, 23)))
        )
        for test in tests:
            side, dollars, cents, expected = test
            x = make(side, _amount.make(dollars, cents))
            self.assertEqual(expected, x)

    def test_add(self):
        tests = (
            #(("debit", 100, 10), ("debit", 1, 2), ("debit", 101, 12)),
            #(("debit", 100, 10), ("credit", 1, 2), ("debit", 99, 8)),
            (("debit", 100, 10), ("credit", 101, 12), ("credit", 1, 2)),
            (("credit", 100, 10), ("credit", 1, 2), ("credit", 101, 12)),
            (("credit", 100, 10), ("debit", 1, 2), ("credit", 99, 8)),
            (("credit", 100, 10), ("debit", 101, 12), ("debit", 1, 2)),
        )
        for test in tests:
            a, b, c = test
            def _make(x): return Entry(x[0], _amount.make(x[1], x[2]))  
            x = _make(a)
            y = _make(b)
            expected = _make(c)
            r = add(x, y)
            self.assertEqual(expected, r)

if __name__ == "__main__":
    unittest.main()


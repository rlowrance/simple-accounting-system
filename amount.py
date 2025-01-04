import collections
import unittest

Amount = collections.namedtuple('Amount', 'dollars cents')

def make(dollars = None, cents = None) -> Amount:
    if dollars is None:
        return make(0, cents)
    if cents is None:
        return make(dollars, 0)
    assert cents >= 0
    return Amount(dollars, cents)

def add(lhs, rhs) -> Amount:
    assert isinstance(lhs, Amount)
    assert isinstance(rhs, Amount)
    return _normalize(Amount(lhs.dollars + rhs.dollars, lhs.cents + rhs.cents))

def subtract(lhs, rhs) -> Amount:
    assert isinstance(lhs, Amount)
    assert isinstance(rhs, Amount)
    return _normalize(Amount(lhs.dollars - rhs.dollars, lhs.cents - rhs.cents))

def greater(lhs, rhs) -> bool:
    assert isinstance(lhs, Amount)
    assert isinstance(rhs, Amount)
    if lhs.dollars > rhs.dollars:
        return True
    if lhs.dollars == rhs.dollars and lhs.cents > rhs.cents:
        return True
    return False

def _normalize(lhs) -> Amount:
    assert isinstance(lhs, Amount)
    if lhs.cents > 99:
        return _normalize(Amount(lhs.dollars + 1, lhs.cents - 100))
    if lhs.cents < 0:
        return _normalize(Amount(lhs.dollars - 1, lhs.cents + 100))
    return lhs

class Test(unittest.TestCase):
    def test_normalize(self):
        tests = (
            ((100, 10), (100, 10)),
            ((-100, 10), (-100, 10)),
            ((100, 101), (101, 1)),
            ((100, 100), (101, 0)),
            ((-1, -10), (-2, 90)),
        )
        for test in tests:
            a, b = test
            x = Amount(a[0], a[1])
            expected = Amount(b[0], b[1])
            r = _normalize(x)
            self.assertEqual(expected, r)

    def test_subtract(self):
        tests = (
            ((100, 10), (1, 2), (99, 8)),
            ((100, 10), (101, 8), (-1, 2)),
            ((100, 10), (201, 12), (-102, 8))
        )

    def test_greater(self):
        tests = (
            ((100, 10), (101, 12), False),
            ((100, 10), (100, 9), True),
            ((100, 10), (100, 10), False),
        )
        for test in tests:
            a, b, expected = test
            def _make(x): return Amount(x[0], x[1])
            x = _make(a)
            y = _make(b)
            self.assertEqual(expected, greater(x, y))

    def test_make(self):
        tests = (
            (None, 50, 0, 50),
            (100, None, 100, 0),
            (100, 50, 100, 50),
        )
        for test in tests:
            d, c, expected_d, expected_c = test
            amount = make(dollars = d, cents=c)
            self.assertEqual(amount.dollars, expected_d)
            self.assertEqual(amount.cents, expected_c)

    def test_add(self):
        tests = (
            ((100, 99), (0, 0), (100, 99)),
            ((100, 99), (0, 1), (101, 0)),
            ((100, 99), (0, 2), (101, 1)),
        )
        for test in tests:
            a, b, c = test
            def _make(x): return Amount(x[0], x[1])
            x = _make(a)
            y = _make(b)
            expected = _make(c)
            self.assertEqual(expected, add(x, y))

if __name__ == "__main__":
    unittest.main()

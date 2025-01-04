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

def add_to_amount(lhs, rhs) -> Amount:
    assert isinstance(lhs, Amount)
    assert isinstance(rhs, Amount)
    return _normalize(make(dollars = lhs.dollars + rhs.dollars,
                           cents = lhs.cents + rhs.cents))

def _normalize(amount) -> Amount:
    assert isinstance(amount, Amount)
    if amount.cents > 100:
        return _normalize(make(dollars = amount.dollars + 1,
                               cents = amount.cents - 100))
    return amount

class Test(unittest.TestCase):
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

    def test_add_to_amount(self):
        tests = (
            (100, 99, 0, 2, 101, 1),
        )
        for test in tests:
            xd, xc, yd, yc, ed, ec = test
            x = make(xd, xc)
            y = make(yd, yc)
            expected = make(ed, ec)
            self.assertEqual(expected, add_to_amount(x, y))

if __name__ == "__main__":
    unittest.main()

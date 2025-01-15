from dataclasses import dataclass

import unittest

from accountingsystemerror import AccountingSystemError

@dataclass
class Amount:
    dollars: int = 0
    cents: int = 0

    def __post_init__(self):
        assert isinstance(self.dollars, int)
        assert isinstance(self.cents, int)
        if self.cents < 0: self._normalize()

    def __str__(self):
        cents_str = f'{self.cents}'.rjust(2, '0')
        return f'{self.dollars}.{cents_str}'


    @staticmethod
    def zero() -> 'Amount':
        return Amount(dollars=0, cents=0)

    def add(self, other: 'Amount') -> 'Amount':
        assert isinstance(other, Amount)
        return Amount(dollars=self.dollars+other.dollars, cents=self.cents+other.cents)._normalize()
    
    def subtract(self, other: 'Amount') -> 'Amount':
        assert isinstance(other, Amount)
        return Amount(dollars=self.dollars-other.dollars, cents=self.cents-other.cents)._normalize()
    
    def greater(self, other: 'Amount') -> bool:
        if self.dollars > other.dollars: return True
        if self.dollars == other.dollars and self.cents > other.cents: return True
        return False
    
    def _normalize(self) -> 'Amount':
        if self.cents > 99: return Amount(dollars=self.dollars+1, cents=self.cents-100)._normalize()
        if self.cents < 0: return Amount(dollars=self.dollars-1, cents=self.cents+100)._normalize()
        return self

class Test(unittest.TestCase):
    def test_str(self):
        tests = (
            (Amount(dollars=0, cents=1), '0.01'),
            (Amount(dollars=1, cents=2), '1.02'),
            (Amount(dollars=123, cents=45), '123.45'),
        )
        for test in tests:
            x, expected = test
            self.assertEqual(expected, f'{x}')
            
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
            r = x._normalize()
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
            r = x.greater(y)
            self.assertEqual(expected, x.greater(y))

    def test_Amount(self):
        tests = (
            (0, 50, 0, 50),
            (100, 0, 100, 0),
            (100, 50, 100, 50),
        )
        for test in tests:
            d, c, expected_d, expected_c = test
            amount = Amount(dollars = d, cents=c)
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
            self.assertEqual(expected, x.add(y))

if __name__ == "__main__":
    unittest.main()

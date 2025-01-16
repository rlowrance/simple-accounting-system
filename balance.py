from typing import Self

import dataclasses
import unittest

from amount import Amount

@dataclasses.dataclass(frozen=True)
class Balance:
    side: str
    amount: Amount

    def __post_init__(self):
        assert isinstance(self.amount, Amount)
        assert isinstance(self.side, str)
        assert self.side in {'debit', 'credit'}

    def add(self, other: Self) -> Self:
        assert isinstance(other, Balance)
        if self.side == other.side: 
            return self.replace(amount=self.amount.add(other.amount))
        if self.amount.greater(other.amount):
            return self.replace(side=self.side, amount=self.amount.subtract(other.amount))
        else:
            return self.replace(side=other.side, amount=other.amount.subtract(self.amount))


    def replace(self, **kwargs) -> Self:
        return dataclasses.replace(self, **kwargs)

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
            def _make(x): return Balance(side=x[0],
                                         amount=Amount(dollars=x[1], cents=x[2]))
            x = _make(a)
            y = _make(b)
            expected = _make(c)
            actual = x.add(y)
            self.assertEqual(expected.side, actual.side)
            self.assertEqual(expected.amount, actual.amount)


if __name__ == '__main__':
    unittest.main()
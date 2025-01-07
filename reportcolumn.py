from collections.abc import Sequence
from dataclasses import dataclass
from typing import List, NamedTuple
import unittest

from accountingsystemerror import AccountingSystemError

@dataclass(frozen=True)
class ReportColumn:
    items: Sequence
    alignment: str

    def __post_init__(self):
        assert len(self.items) > 0
        assert self.alignment in {'left', 'right'}


ReportColumn1 = NamedTuple('ReportColumn', [('items', list), ('alignment', str)])
# the items are typically a string, the header, followed by the values (of any type) in the column
# ex: ['account category', 'asset', 'asset', 'liability']
# ex: ['amount', 10, 30, 1.23]

def make(items: list, alignment: str) -> ReportColumn:
    assert isinstance(items, Sequence)
    assert len(items) > 0  # require at least the header
    assert alignment in {"left", "right"}
    return ReportColumn(items=items, alignment=alignment)

class Test(unittest.TestCase):
    def test(self):
        # x = make(items=['header', 10, 30], alignment="right")
        x = ReportColumn(items=['header, 10, 30'], alignment='right')
        self.assertTrue(isinstance(x, ReportColumn))

if __name__ == '__main__':
    unittest.main()
        
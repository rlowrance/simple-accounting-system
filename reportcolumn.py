from collections.abc import Sequence
from dataclasses import dataclass
import unittest

@dataclass(frozen=True)
class ReportColumn:
    items: Sequence
    alignment: str

    def __post_init__(self):
        assert len(self.items) > 0
        assert self.alignment in {'left', 'right'}

    def render(self, column_spacing=1) -> tuple[str]:
        width = max(map(lambda x: len(f'{x}'), self.items))
        r = []
        for item in self.items:
            s = f'{item}'
            aligned_item = s.ljust(width) if self.alignment == 'left' else s.rjust(width)
            r.append(aligned_item)
        return tuple(r)


class Test(unittest.TestCase):
    def test_init(self):
        # x = make(items=['header', 10, 30], alignment="right")
        x = ReportColumn(items=['header, 10, 30'], alignment='right')
        self.assertTrue(isinstance(x, ReportColumn))

    def test_render(self):
        items = ('header', 10, 20.2, 'abc')
        tests = (
            ReportColumn(alignment='left', items=items),
            ReportColumn(alignment='right', items=items),
        )
        for test in tests:
            lines = test.render()
            self.assertEqual(4, len(lines))
            self.assertEqual(6, len(lines[0]))

if __name__ == '__main__':
    unittest.main()
        
# Align csv lines so that they can be viewed in a text editor in lined-up columns
from dataclasses import dataclass
from typing import Any, Sequence, Self, List, Tuple

import copy
import unittest

@dataclass(frozen=True, kw_only=True)
class AlignedCSV:
    alignments: Sequence[str]
    _max_widths: Sequence[int] = None
    _data: Sequence[Sequence[str]] = None

    def __post_init__(self):
        for alignment in self.alignments:
            assert alignment in ('left', 'right')
    
    # just save the data
    def join(self, row: Sequence) -> Self:
        if self._max_widths is not None:
            assert len(self._max_widths) == len(row)
        if self._max_widths is None:
            old_max_widths = []
            for _ in row:
                old_max_widths.append(0)
        else:
            old_max_widths = self._max_widths

        new_row_s = []
        new_max_widths = []
        for i, x in enumerate(row):
            s = f'{x}'
            new_max_widths.append(max(len(s), old_max_widths[i]))
            new_row_s.append(s)
        new_data = [] if self._data is None else list(copy.deepcopy(self._data))
        new_data.append(new_row_s)
        return AlignedCSV(
            alignments=self.alignments,
            _max_widths=tuple(new_max_widths),
            _data=tuple(new_data))

    # align the columns
    def cast(self, to: str) -> Any:
        if to == 'tuple(tuple)': return self._cast_to_tuple_tuple()
        raise NotImplementedError(f'{to}')

    def _cast_to_tuple_tuple(self) -> Tuple[Tuple]:
        r = []
        for row in self._data:
            line = []
            for i, item in enumerate(row):
                width = self._max_widths[i]
                line.append(item.ljust(width) if self.alignments[i] == 'left' else item.rjust(width))
            r.append(tuple(line))
        r = tuple(r)
        return r


class Test(unittest.TestCase):
    def test(self):
        verbose = False
        r = AlignedCSV(alignments=('left', 'right'))
        r = r.join(('field name', 'value'))  # header
        r = r.join(('abc', 0.13))
        r = r.join(('a long field value', 1234.56))
        if verbose:
            for line in r.cast('tuple(tuple)'):
                print(line)
        self.assertTrue(True)  # mark completion

if __name__ == '__main__':
    unittest.main()
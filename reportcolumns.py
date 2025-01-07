from collections.abc import Sequence
import copy
from dataclasses import dataclass
import dataclasses
from typing import NamedTuple, List, Self, Tuple
import unittest

from accountingsystemerror import AccountingSystemError
from reportcolumn import ReportColumn

@dataclass(frozen=True)
class ReportColumns:
    columns: tuple = ()

    def __post_init__(self):
        if len(self.columns) == 0: return
        expected_len = len(self.columns[0])
        for column in self.columns:
            assert expected_len == len(column)

    def join(self, report_column: ReportColumn) -> Self:
        assert isinstance(report_column, ReportColumn)
        if len(self.columns) > 0:
            assert len(report_column.items) == len(self.columns[0])

        def to_text(x): return f'{x}'
        texts = list(map(to_text, report_column.items))
        widths = map(len, texts)
        max_width = max(widths)

        def aligned(s: str) -> str:
            if report_column.alignment == 'left': return s.ljust(max_width)
            if report_column.alignment == 'right': return s.rjust(max_width)
            return s  # avoid a type-checker message
        aligned_texts = list(map(aligned, texts))
        
        new_columns = self.columns + (aligned_texts,)
        return dataclasses.replace(self, columns=new_columns)

    # Return tuple of strings that are the report lines
    def render(self, column_spacing=1) -> tuple:
        assert len(self.columns) > 0
        r = []
        for column_index in range(len(self.columns[0])):
            line_fields = []
            for column in self.columns:
                if len(line_fields) > 0:
                    line_fields.append(' '.ljust(column_spacing))
                line_fields.append(column[column_index])
            line = ''.join(line_fields)
            r.append(line)
        return tuple(r)
    

class Test(unittest.TestCase):
    def test(self):
        tests = (
            ('left', ('header1', 101, 202, 'abc')),
            ('right', ('header2', 201, 202, 'abc')),
        )
        rc = ReportColumns()
        for test in tests:
            alignment: str = test[0]
            items: tuple = test[1]
            next_column = ReportColumn(items, alignment)
            rc = rc.join(next_column)
        lines = rc.render(column_spacing=2)
        if False:
            for line in lines:
                print(line)
        self.assertTrue(isinstance(rc, ReportColumns))

if __name__ == '__main__':
    unittest.main()
        
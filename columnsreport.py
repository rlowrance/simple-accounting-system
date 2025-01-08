from collections.abc import Sequence
from dataclasses import dataclass
import dataclasses
from typing import Self
import unittest

from accountingsystemerror import AccountingSystemError
from reportcolumn import ReportColumn

@dataclass(frozen=True)
class ColumnsReport:
    columns: tuple[ReportColumn] = tuple()
    column_length: int = 0

    def __post_init__(self):
        if len(self.columns) == 0: return
        for column in self.columns:
            assert isinstance(column, ReportColumn)
        expected_len = len(self.columns[0].items)
        for column in self.columns:
            assert expected_len == len(column.items)

    def join(self, report_column: ReportColumn) -> Self:
        assert isinstance(report_column, ReportColumn)
        if self.column_length != 0:
            assert self.column_length == len(report_column.items)
        # new_columns has type tuple[ReportColumn, ReportColumn]
        # new_columns = self.columns + (report_column,)
        # work around the above typing error from pylance
        new_columns = list(self.columns)
        new_columns.append(report_column)
        new_columns = tuple(new_columns)
        return ColumnsReport(columns=new_columns, column_length=len(report_column.items))


    # Return tuple of strings that are the report lines
    def render(self, column_spacing=1) -> tuple[str]:
        assert len(self.columns) > 0
        rendered_columns = tuple(map(lambda x: x.render(), self.columns))
        r = []  # each item will be a line
        for row_index in range(self.column_length):
            line = []
            for rendered_column in rendered_columns:
                if len(line) > 0: line.append(' '.rjust(column_spacing))
                line.append(rendered_column[row_index])
            rendered_line = ''.join(line)
            r.append(rendered_line)
        renderer_report = tuple('\n'.join(r))
        return renderer_report
    

class Test(unittest.TestCase):
    def test_join_render(self):
        tests = (
            ('left', ('header1', 101, 202, 'abc')),
            ('right', ('header2', 201, 202, 'abc')),
        )
        rc = ColumnsReport()
        for test in tests:
            alignment: str = test[0]
            items: tuple = test[1]
            next_column = ReportColumn(items, alignment)
            rc = rc.join(next_column)
        lines = rc.render(column_spacing=2)
        if False:
            for line in lines:
                print(line)
        self.assertTrue(isinstance(rc, ColumnsReport))


if __name__ == '__main__':
    unittest.main()
        
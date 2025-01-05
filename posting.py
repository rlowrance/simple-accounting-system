import collections
import datetime
import unittest

from accountingsystemerror import AccountingSystemError
import amount
import entry as entry_

Posting = collections.namedtuple('Posting', 'date entry description source source_location')

def make(date=None, entry=None, description=None, source=None, source_location=None) -> Posting:
    if date is None:
        raise AccountingSystemError(f'missing date')
    if not isinstance(date, datetime.date):
        raise AccountingSystemError(f'date {date} is not a datetime.date')
    if entry is None:
        raise AccountingSystemError(f'missing entry')
    if not isinstance(entry, entry_.Entry):
        raise AccountingSystemError(f'entry {entry} is not an Entry')
    if description is None:
        raise AccountingSystemError(f'missing description')
    if not isinstance(description, str):
        raise AccountingSystemError(f'description {description} is not a str')
    if source is None:
        raise AccountingSystemError(f'missing source')
    if not isinstance(source, str):
        raise AccountingSystemError(f'source {source} is not a str')
    if source_location is None:
        raise AccountingSystemError(f'missing source_location')
    if not isinstance(source_location, str):
        raise AccountingSystemError(f'source_location {source_location} is not a str')
    return Posting(date, entry, description, source, source_location)

class Test(unittest.TestCase):
    def test_make(self):
        x = make(date=datetime.date(1,1,1), 
                 entry=entry_.make(side="debit", amount=amount.make(dollars=100, cents=10)),
                 description="something",
                 source="source",
                 source_location="location")
        self.assertTrue(True)  # just test run to completion

if __name__ == '__main__':
    unittest.main()
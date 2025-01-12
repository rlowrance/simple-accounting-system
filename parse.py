# parse input file lines into acount declarations and journal entries

import copy
import csv
import dataclasses
import datetime
import unittest

from dataclasses import dataclass
from typing import List, Self, Union

from accountdeclaration import AccountDeclaration
from amount import Amount
from journalentry import JournalEntry
from line import Line

# ref: https://stackoverflow.com/questions/3305926/python-csv-string-to-array
def csv_line_to_str(line: str) -> List[str]:
    return list(map(str.strip, next(csv.reader([line]))))

# ref: https://stackoverflow.com/questions/3305926/python-csv-string-to-array
def csv_line_from_row(row: List[str]) -> str:
    with io.StringIO() as line:
        csv.writer(line).writerow(row)
        return line.getvalue().strip()

        # ref: https://stackoverflow.com/questions/6330071/safe-casting-in-python
def safe_cast(value, to_type, default_value=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default_value

# ref: https://stackoverflow.com/questions/4071396/how-to-split-by-comma-and-strip-white-spaces-in-python
def split_and_strip(s, splitter=None) -> list:
    if splitter is None:
        return list(map(str.strip, s.split()))
    return list(map(str.strip, s.split(splitter)))

@dataclass(frozen=True)
class DateComponents:
    year: Union[None, int] = None
    month: Union[None, int] = None
    day: Union[None, int] = None

    @classmethod
    def from_string(cls, s: str) -> Self:
        if len(s) == 8: return DateComponents(year=int(s[0:4]), month=int(s[4:6]), day=int(s[6:8]))
        if len(s) == 4: return DateComponents(month=int(s[0:2]), day=int(s[2:4]))
        if len(s) == 2: return DateComponents(day=int(s))
        if len(s) == 0: return DateComponents()
        raise ValueError(f'date {s} is not of form YYYYMMDD or MMDD or DD')


    def is_complete(self) -> bool:
        return self.year is not None and self.month is not None and self.day is not None

    def to_date(self) -> datetime.date:
        assert isinstance(self.year, int)
        assert isinstance(self.month, int)
        assert isinstance(self.day, int)
        return datetime.date(self.year, self.month, self.day)

    def replace(self, **kwargs) -> Self:
        return dataclasses.replace(self, **kwargs)

def make_amount(s: str) -> Amount:
    splits = split_and_strip(s, ".")
    if len(splits) == 1: # ex: 123
        dollars = safe_cast(splits[0], int)
        if dollars is None: raise ValueError(f'dollar amount {splits[0]} is not an int')
        return Amount(dollars=dollars, cents=0)
    if len(splits) == 2: # ex: 123.45
        a, b = splits
        dollars = safe_cast(a, int)
        cents = safe_cast(b, int)
        if dollars is None:
            raise ValueError(f'dollars amount {a} is not an int')
        if cents is None:
            raise ValueError(f'cents amount {b} is not an int')
        return Amount(dollars=dollars, cents=cents)
    raise ValueError(f's {s} is not like 123.45 (specifying dollars and cents)')

def parse_account_declaration(s: str) -> AccountDeclaration:
    splits = split_and_strip(s, splitter=':')
    if len(splits) == 2: return AccountDeclaration(category=splits[0], name=splits[1])
    raise ValueError(f'account declaration not like Asset:cash; found: {s}')

def make_journal_entry(splits: List[str]) -> JournalEntry:
    assert len(splits) == 5
    return JournalEntry(
        date=datetime.date.fromisoformat(splits[0]),
        amount=make_amount(splits[1]),
        debit_account=splits[2],
        credit_account=splits[3],
        description=splits[4],
        source='',
        source_location=''
    )
    # synthesize missing splits
    new_splits = copy.deepcopy(splits)
    new_splits.append('')
    return make_journal_entry(new_splits)

def parse(line: Line, last_journal_entry: Union[JournalEntry, None]) -> Union[AccountDeclaration, JournalEntry]:
    def complete(je: JournalEntry) -> JournalEntry:
        return dataclasses.replace(je, source=line.source, source_location=line.source_location)
    splits = csv_line_to_str(line.text)  # allow quoting and other CSV file layout conventions
    if len(splits) == 1: 
        return parse_account_declaration(line.text)
    else:
        while len(splits) < 5:
            splits.append('')
        date_s, amount_s, debit_account_s, credit_account_s, description_s = splits
        date_components = DateComponents.from_string(date_s)
        if not date_components.is_complete():
            if last_journal_entry is None:
                raise ValueError(f'invalid date {date_s}')
            def fill(x, y): return y if x is None else x
            date_components = dataclasses.replace(
                date_components,
                year=fill(date_components.year, last_journal_entry.date.year),
                month=fill(date_components.month, last_journal_entry.date.month),
                day=fill(date_components.day, last_journal_entry.date.day)
            )
        date = date_components.to_date()

        if last_journal_entry is None:
            return JournalEntry(
                date=date,
                amount=make_amount(amount_s),
                debit_account=debit_account_s,
                credit_account=credit_account_s,
                description=description_s,
                source=line.source,
                source_location=line.source_location
            )
        else:
            return JournalEntry(
                date=date,
                amount=make_amount(amount_s) if len(amount_s) > 0 else last_journal_entry.amount,
                debit_account=debit_account_s if len(debit_account_s) > 0 else last_journal_entry.debit_account,
                credit_account=credit_account_s if len(credit_account_s) > 0 else last_journal_entry.credit_account,
                description=description_s if len(description_s) >0 else last_journal_entry.description,
                source=line.source,
                source_location=line.source_location
            )

class Test(unittest.TestCase):
    def test_parse_journal_entry_line(self):
        expected = JournalEntry(
            date=datetime.date(2025,12,25),
            amount=Amount(dollars=123, cents=45),
            debit_account='cash',
            credit_account='owners equity',
            description='description',
            source='source',
            source_location='source_location')
        tests = (
            ',123.45',
            ',,,,',
            ',,,',
            '25,',
            '1225,',
            ',123.45',
            ',,cash',
            ',,, owners equity',
            ',,,owners equity   ,',
            ',,,,description    ',
        )
        for test in tests:
            line = Line(test, source='source', source_location='source_location')
            r = parse(line=line, last_journal_entry=expected)
            self.assertTrue(isinstance(r, JournalEntry))
            assert isinstance(r, JournalEntry)
            self.assertEqual(expected.date, r.date)
            self.assertEqual(expected.amount, r.amount)
            self.assertEqual(expected.debit_account, r.debit_account)
            self.assertEqual(expected.credit_account, r.credit_account)
            self.assertEqual(expected.description, r.description)
            self.assertEqual(expected.source, r.source)
            self.assertEqual(expected.source_location, r.source_location)

    def test_parse_csv_line(self):
        tests = (
            ('1, 2, 3', ['1', '2', '3']),
            ('1,    2  ,     3', ['1', '2', '3']),
        )
        for test in tests:
            x, expected = test
            self.assertEqual(expected, csv_line_to_str(x))

if __name__ == '__main__':
    unittest.main()

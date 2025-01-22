# utility functions
import csv
import io
import sys
import unittest

from typing import Any, Dict, List, Set


# ref: https://stackoverflow.com/questions/3305926/python-csv-string-to-array
def csv_line_from_row(row: List[str]) -> str:
    with io.StringIO() as line:
        csv.writer(line).writerow(row)
        return line.getvalue().strip()

# ref: https://stackoverflow.com/questions/3305926/python-csv-string-to-array
def csv_line_to_str(line: str) -> List[str]:
    return list(map(str.strip, next(csv.reader([line]))))

# Write to stderr
# ref: https://stackoverflow.com/questions/5574702/how-do-i-print-to-stderr-in-python
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# ref: https://stackoverflow.com/questions/483666/reverse-invert-a-dictionary-mapping
def invert_dict(d: Dict[Any, Any]) -> Dict[Any, Set]:
    r = {}
    for k, v in d.items():
        r.setdefault(v, set()).add(k)
    return r

# ref: https://stackoverflow.com/questions/2937114/python-check-if-an-object-is-a-sequence
def is_sequence(obj) -> bool:
    try:
        len(obj)
        obj[0:0]
        return True
    except TypeError:
        return False

# ref: https://stackoverflow.com/questions/6330071/safe-casting-in-python
def safe_cast(value, to_type, default_value=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default_value

# ref: https://stackoverflow.com/questions/4071396/how-to-split-by-comma-and-strip-white-spaces-in-python
def split_and_strip(s, splitter=None) -> List:
    if splitter is None:
        return list(map(str.strip, s.split()))
    return list(map(str.strip, s.split(splitter)))


class Maybe: # ref https://dev.to/nhradek/monads-in-python-4npa
    def __init__(self, value): self.value = value
    def __repr__(self): return f'Maybe({self.value})'
    def unwrap(self): return self.value
    def bind(self, func): return Maybe(None) if self.value is None else Maybe(func(self.value))
    @staticmethod
    def wrap(value): return Maybe(value)

class Test(unittest.TestCase):
    def test_csv_line_to_str(self):
        tests = (
            ('1, 2, 3', ['1', '2', '3']),
            ('1,    2  ,     3', ['1', '2', '3']),
        )
        for test in tests:
            x, expected = test
            self.assertEqual(expected, csv_line_to_str(x))

if __name__ == '__main__':
    unittest.main()
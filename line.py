import collections
import unittest

from accountingsystemerror import AccountingSystemError

Line = collections.namedtuple('Line', 'text source source_location')

def make(text=None, source=None, source_location=None) -> Line:
    def is_type(name, value, type):
        if not isinstance(value, type):
            raise AccountingSystemError(f'argument {name} with value {value} is not an instance of {type}')
    is_type('text', text, str)
    is_type('source', source, str)
    is_type('source_location', source_location, str)
    return Line(text, source, source_location)

class Test(unittest.TestCase):
    def test(self):
        tests = (
            ('text', 'file', 'line'),
        )
        for test in tests:
            a, b, c = test
            r = make(text=a, source=b, source_location=c)
            self.assertEqual(a, r.text)
            self.assertEqual(b, r.source)
            self.assertEqual(c, r.source_location)

if __name__ == '__main__':
    unittest.main()

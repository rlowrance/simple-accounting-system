import collections
from dataclasses import dataclass
import unittest

@dataclass(frozen=True)
class Line:
    text: str = ''
    source: str = ''
    source_location: str = ''

    def __post_init__(self):
        assert isinstance(self.text, str)
        assert isinstance(self.source, str)
        assert isinstance(self.source_location, str)

class Test(unittest.TestCase):
    def test(self):
        tests = (
            ('text', 'file', 'line'),
        )
        for test in tests:
            a, b, c = test
            r = Line(text=a, source=b, source_location=c)
            self.assertEqual(a, r.text)
            self.assertEqual(b, r.source)
            self.assertEqual(c, r.source_location)

if __name__ == '__main__':
    unittest.main()

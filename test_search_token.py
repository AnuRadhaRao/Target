import unittest

from DocumentSearch import search_token


class TestSum(unittest.TestCase):
    def test_string_match(self):
        search_term = "Hitchhiker's"
        result = string_match(search_term)
        self.assertEqual(result['sample_text/hitchhikers.txt'], 6)

if __name__ == '__main__':
    unittest.main()
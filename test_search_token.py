import unittest

from search_token import string_match, regex_match, indexed_search


class TestStringMethods(unittest.TestCase):

    def test_string_match_hitchiker(self):
        result = string_match("hitchhiker's")
        # print(result)
        self.assertEqual(result['hitchhikers.txt'], 6)

    def test_string_match_warp(self):
        result = string_match("warp")
        # print(result)
        self.assertEqual(result['warp_drive.txt'], 6)

    def test_string_match_armed_forces(self):
        result = string_match("french")
        # print(result)
        self.assertEqual(result['french_armed_forces.txt'], 11)
    
    def test_string_match_no_match(self):
        result = string_match("extreme")
        # print(result)
        self.assertEqual(result['french_armed_forces.txt'], 0)
    
    def test_string_match_whole_words_only(self):
        # "art" appears inside other words but never on its own
        result = string_match("art")
        self.assertEqual(result['hitchhikers.txt'], 0)

    def test_string_match_finds_phrase(self):
        # 6 mentions of "Hitchhiker's", one of them without "Guide" after it
        result = string_match("hitchhiker's guide")
        self.assertEqual(result['hitchhikers.txt'], 5)

    def test_regex_match_french(self):
        result = regex_match("Franc.-")
        # print(result)
        self.assertEqual(result['french_armed_forces.txt'], 3)
    
    def test_regex_match_hitchhiker(self):
        result = regex_match(r"\[\d\]")
        # print(result)
        self.assertEqual(result['hitchhikers.txt'], 5)
    
    def test__regex_match_warp(self):
        result = regex_match(r"\([^\"]*\)")
        # print(result)
        self.assertEqual(result['warp_drive.txt'], 2)

    def test_regex_match_is_case_insensitive(self):
        upper = regex_match("FRENCH")
        lower = regex_match("french")
        self.assertEqual(upper, lower)
        self.assertGreater(upper['french_armed_forces.txt'], 0)

    def test_indexed_match_french(self):
        result = indexed_search("conflicts")
        # print(result)
        self.assertEqual(result['french_armed_forces.txt'], 4)
    
    def test_indexed_match_hitchhiker(self):
        result = indexed_search("Guide")
        # print(result)
        self.assertEqual(result['hitchhikers.txt'], 8)

    def test_indexed_match_keeps_apostrophes(self):
        result = indexed_search("Hitchhiker's")
        self.assertEqual(result['hitchhikers.txt'], 6)

    def test_string_and_indexed_agree_on_single_words(self):
        for word in ["the", "guide", "hitchhiker", "warp", "conflicts"]:
            self.assertEqual(string_match(word), indexed_search(word), word)

    def test_indexed_match_warp(self):
        result = indexed_search("blue")
        # print(result)
        self.assertEqual(result['warp_drive.txt'], 0)
 
if __name__ == '__main__':
    unittest.main()
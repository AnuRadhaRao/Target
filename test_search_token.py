import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from search_token import indexed_search, main, regex_match, string_match


class TestStringMethods(unittest.TestCase):

    def test_string_match_hitchiker(self):
        result = string_match("hitchhiker's")
        self.assertEqual(result['hitchhikers.txt'], 6)

    def test_string_match_warp(self):
        result = string_match("warp")
        self.assertEqual(result['warp_drive.txt'], 6)

    def test_string_match_armed_forces(self):
        result = string_match("french")
        self.assertEqual(result['french_armed_forces.txt'], 11)
    
    def test_string_match_no_match(self):
        result = string_match("extreme")
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
        self.assertEqual(result['french_armed_forces.txt'], 3)
    
    def test_regex_match_hitchhiker(self):
        result = regex_match(r"\[\d\]")
        self.assertEqual(result['hitchhikers.txt'], 5)
    
    def test__regex_match_warp(self):
        result = regex_match(r"\([^\"]*\)")
        self.assertEqual(result['warp_drive.txt'], 2)

    def test_regex_match_is_case_insensitive(self):
        upper = regex_match("FRENCH")
        lower = regex_match("french")
        self.assertEqual(upper, lower)
        self.assertGreater(upper['french_armed_forces.txt'], 0)

    def test_indexed_match_french(self):
        result = indexed_search("conflicts")
        self.assertEqual(result['french_armed_forces.txt'], 4)
    
    def test_indexed_match_hitchhiker(self):
        result = indexed_search("Guide")
        self.assertEqual(result['hitchhikers.txt'], 8)

    def test_indexed_match_keeps_apostrophes(self):
        result = indexed_search("Hitchhiker's")
        self.assertEqual(result['hitchhikers.txt'], 6)

    def test_string_and_indexed_agree_on_single_words(self):
        for word in ["the", "guide", "hitchhiker", "warp", "conflicts"]:
            self.assertEqual(string_match(word), indexed_search(word), word)

    def test_indexed_match_warp(self):
        result = indexed_search("blue")
        self.assertEqual(result['warp_drive.txt'], 0)
 
    def test_cli_ranks_files_by_matches(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["--method", "string", "warp"]), 0)
        first_line = out.getvalue().splitlines()[0]
        self.assertTrue(first_line.startswith("warp_drive.txt"), first_line)

    def test_cli_rejects_bad_regex(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--method", "regex", "("]), 2)

    def test_cli_rejects_missing_folder(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--dir", "/no/such/dir", "-m", "string", "x"]), 2)


if __name__ == '__main__':
    unittest.main()
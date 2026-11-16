"""Search a folder of text documents for a term and rank files by match count."""

import argparse
import os
import re
import sys
import time

# default corpus: the sample_text folder next to this script
SEARCH_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_text")

# words are runs of letters/digits, keeping inner apostrophes ("don't")
WORD_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)*")


def normalise(text: str) -> str:
    # lower-case and turn curly apostrophes into straight ones
    return text.lower().replace("’", "'")


def list_documents() -> list:
    return sorted(
        name
        for name in os.listdir(SEARCH_DIRECTORY)
        if os.path.isfile(os.path.join(SEARCH_DIRECTORY, name))
    )


def read_document(filename: str) -> str:
    with open(os.path.join(SEARCH_DIRECTORY, filename), encoding="utf-8") as document:
        return normalise(document.read())


def tokenize(text: str) -> list:
    return WORD_PATTERN.findall(normalise(text))


def string_match(token: str) -> dict:
    """Count whole-word / whole-phrase occurrences of token in each document."""
    # "art" must not count inside "party" or "art's"
    term = re.escape(normalise(token))
    pattern = re.compile(r"(?<![a-z0-9])(?<![a-z0-9]')" + term + r"(?!'?[a-z0-9])")
    return {name: len(pattern.findall(read_document(name))) for name in list_documents()}


def regex_match(regex: str) -> dict:
    """Count case-insensitive matches of a regular expression in each document."""
    pattern = re.compile(regex, re.IGNORECASE)
    return {name: len(pattern.findall(read_document(name))) for name in list_documents()}


# the index is built once per process and reused by every indexed search
_search_index = None


def build_index() -> dict:
    """Return {filename: {word: count}} for every document."""
    search_index = {}
    for name in list_documents():
        glossary = {}
        for word in tokenize(read_document(name)):
            glossary[word] = glossary.get(word, 0) + 1
        search_index[name] = glossary
    return search_index


def get_index(rebuild: bool = False) -> dict:
    global _search_index
    if _search_index is None or rebuild:
        _search_index = build_index()
    return _search_index


def indexed_search(token: str) -> dict:
    """Look up a single word in the prebuilt index."""
    # the index holds single words, so normalise the search term the same way
    terms = tokenize(token)
    return {
        name: index.get(terms[0], 0) if len(terms) == 1 else 0
        for name, index in get_index().items()
    }


METHODS = {
    "string": string_match,
    "regex": regex_match,
    "indexed": indexed_search,
}
MENU = {"1": "string", "2": "regex", "3": "indexed"}


def print_results(results: dict) -> None:
    for name, count in sorted(results.items(), key=lambda item: item[1], reverse=True):
        print(name, "------>", count, "matches")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("term", nargs="?", help="term, phrase or regex to search for")
    parser.add_argument("-m", "--method", choices=METHODS, help="search method")
    parser.add_argument("-d", "--dir", help="folder of documents (default: sample_text)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    global SEARCH_DIRECTORY, _search_index
    args = parse_args(argv)
    if args.dir:
        if not os.path.isdir(args.dir):
            print(f"Not a folder: {args.dir}", file=sys.stderr)
            return 2
        SEARCH_DIRECTORY = args.dir
        _search_index = None

    # no flags given: fall back to the original interactive prompts
    method = args.method
    if method is None:
        choice = input(
            "Choose a search method: 1. String Match 2. Regular Expression 3. Indexed : "
        ).strip()
        method = MENU.get(choice)
        if method is None:
            print("Please enter 1, 2 or 3", file=sys.stderr)
            return 2
    term = args.term if args.term is not None else input("Enter your search string: ")
    if not term.strip():
        print("Search string is empty", file=sys.stderr)
        return 2

    start = time.perf_counter()
    try:
        results = METHODS[method](term)
    except re.error as error:
        print(f"Invalid regular expression: {error}", file=sys.stderr)
        return 2
    print_results(results)
    print(f"Elapsed time: {time.perf_counter() - start:.4f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

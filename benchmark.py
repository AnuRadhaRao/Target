"""Time each search method over many random search terms.

The case study asked for 2M searches. String and regex search re-read
every file on each query (a few ms each), so 2M of them takes hours;
use --searches to pick a size, e.g. --searches 2000000 --methods indexed.
"""

import argparse
import random
import time

import search_token

METHODS = {
    "string": search_token.string_match,
    "regex": search_token.regex_match,
    "indexed": search_token.indexed_search,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--searches", type=int, default=1000)
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=list(METHODS))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    # random terms drawn from the corpus, plus some that never match
    rng = random.Random(args.seed)
    vocabulary = sorted({w for index in search_token.build_index().values() for w in index})
    terms = [rng.choice(vocabulary) for _ in range(args.searches)]
    for i in range(0, len(terms), 10):
        terms[i] = "zzz-no-match-%d" % i

    for name in args.methods:
        search = METHODS[name]
        start = time.perf_counter()
        if name == "indexed":
            search_token.get_index(rebuild=True)
        build = time.perf_counter() - start
        for term in terms:
            search(term)
        total = time.perf_counter() - start
        line = (
            f"{name:8} {args.searches} searches in {total:8.3f}s "
            f"({total / args.searches * 1e6:9.1f} us/search"
        )
        if name == "indexed":
            line += f", including {build:.3f}s to build the index"
        print(line + ")")


if __name__ == "__main__":
    main()

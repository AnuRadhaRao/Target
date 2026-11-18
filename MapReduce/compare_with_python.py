"""Check that the Hadoop TermIndex output matches the Python index exactly.

Usage: python MapReduce/compare_with_python.py <TermIndex output dir>
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import search_token  # noqa: E402


def read_hadoop_index(output_dir: str) -> dict:
    index = {}
    for part in sorted(os.listdir(output_dir)):
        if not part.startswith("part-"):
            continue
        with open(os.path.join(output_dir, part), encoding="utf-8") as lines:
            for line in lines:
                word, file_count = line.rstrip("\n").split("\t")
                filename, count = file_count.rsplit("=", 1)
                index.setdefault(filename, {})[word] = int(count)
    return index


def main() -> int:
    hadoop = read_hadoop_index(sys.argv[1])
    python = search_token.build_index()
    if hadoop != python:
        for filename in sorted(set(hadoop) | set(python)):
            h, p = hadoop.get(filename, {}), python.get(filename, {})
            diff = sorted(w for w in set(h) | set(p) if h.get(w) != p.get(w))
            if diff:
                print(f"{filename}: {len(diff)} words differ, e.g. {diff[:5]}")
        return 1
    words = sum(len(index) for index in python.values())
    print(f"OK: {len(python)} files, {words} (file, word) counts match")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Document Search

[![CI](https://github.com/AnuRadhaRao/Target/actions/workflows/ci.yaml/badge.svg)](https://github.com/AnuRadhaRao/Target/actions/workflows/ci.yaml)

Search a folder of text documents for a word, phrase or regular expression,
and list the documents in order of relevance (how many times the term
appears).

This began in 2021 as a case study for a role at Target. In 2026 I came
back to it, fixed the bugs, made the indexed search actually fast, and added
a benchmark, a Hadoop version of the index and CI. The
[original 2021 write-up](Documentation.docx) is kept as it was.

## Search methods

| Method    | Flag         | What counts as a match                                           |
| --------- | ------------ | ---------------------------------------------------------------- |
| String    | `-m string`  | The whole word or phrase, case-insensitive ("art" ≠ "party")     |
| Regex     | `-m regex`   | Each match of a regular expression, case-insensitive             |
| Indexed   | `-m indexed` | A single word, looked up in an index built once per process      |

String and indexed search split text into words the same way (letters and
digits, keeping inner apostrophes such as "hitchhiker's"), so for a single
word they return the same counts. A test checks this.

## Usage

Needs Python 3.10 or newer and no third-party packages.

```sh
python search_token.py -m indexed guide
python search_token.py -m string "hitchhiker's guide"
python search_token.py -m regex 'franc.-'
python search_token.py -m string warp --dir /path/to/other/docs
```

Example output:

```text
hitchhikers.txt ------> 8 matches
french_armed_forces.txt ------> 0 matches
performance_test.txt ------> 0 matches
warp_drive.txt ------> 0 matches
Elapsed time: 0.0665s
```

Run it with no arguments to get the original interactive prompts. Invalid
input (a bad menu choice, an empty term, a broken regex or a missing folder)
prints an error and exits with code 2.

## Performance

The case study asked for 2 million searches with random terms and which
method is fastest. `benchmark.py` does this: it picks random words from the
documents, makes one in ten a word that never matches, and times each method.

```sh
python benchmark.py --searches 500
python benchmark.py --searches 2000000 --methods indexed
```

Results on a small cloud dev container (about 1.5 MB of text):

| Method  | Time per search | 2M searches            |
| ------- | --------------- | ---------------------- |
| String  | ~23 ms          | ~13 hours (estimated)  |
| Regex   | ~9 ms           | ~5 hours (estimated)   |
| Indexed | ~0.9 µs         | 1.8 s, index included  |

The indexed search wins because the expensive part, reading and splitting
every document, happens once (about 50 ms), and each search after that is a
dictionary lookup per document. String and regex search re-read and scan
every file on every query. The 2021 version rebuilt the index on every
search, which made it the slowest of the three; it is now built once and
reused.

## Scaling to large content and 5,000+ requests/second

- **Index ahead of time, not per request.** Build the index when documents
  change and serve searches from it. Request cost then depends on the number
  of matching documents, not on the size of the corpus.
- **Build the index in parallel.** [`MapReduce/`](MapReduce) holds a Hadoop
  job that builds the same index across a cluster. CI checks that its output
  matches the Python index exactly.
- **Shard and replicate.** Split the index by document across shards, query
  shards in parallel and merge the counts. Add replicas behind a load
  balancer to handle more requests per second.
- **Use a search engine for real workloads.** Elasticsearch or Solr already
  do sharded inverted indexes, replicas, relevance scoring and regex queries.
- **Cache popular terms**, since search traffic is usually skewed towards a
  few queries.

## Hadoop index job

`MapReduce/TermIndex.java` is one Hadoop MapReduce job. For every word it
writes how many times it appears in each document
(`guide	hitchhikers.txt=8`). `build.sh` compiles it with plain `javac` and
`jar`, using `hadoop classpath` when Hadoop is installed and otherwise the
jars listed in `MapReduce/jars.txt`.

On a Hadoop cluster:

```sh
MapReduce/build.sh
hadoop jar MapReduce/term-index.jar TermIndex <input dir> <output dir>
```

Without Hadoop installed, `build.sh` downloads the few client jars it needs
into `MapReduce/lib/`, and the job runs in Hadoop local mode:

```sh
MapReduce/build.sh
cd MapReduce
java -cp "term-index.jar:lib/*" TermIndex ../sample_text /tmp/term-index
python compare_with_python.py /tmp/term-index
```

## Development

```sh
python -m unittest -v        # unit and CLI tests
pip install -r requirements-dev.txt && ruff check . && ruff format --check .
```

CI (GitHub Actions) runs lint, the tests on Python 3.10, 3.12 and 3.13, a
short benchmark, and the Hadoop job with the comparison against Python.

## Layout

```text
search_token.py              search functions and CLI
test_search_token.py         tests
benchmark.py                 random-term benchmark
sample_text/                 documents searched by default
MapReduce/                   Hadoop version of the index (jars.txt lists its jars)
Documentation.docx           original 2021 write-up
requirements-dev.txt         dev tools (ruff)
.github/workflows/ci.yaml    CI
```

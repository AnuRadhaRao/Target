import time
import re
import sys
from os import listdir

# path to directory
SEARCH_DIRECTORY = "sample_text"


# words are runs of letters/digits, keeping inner apostrophes ("don't")
WORD_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)*")


def read_document(filename: str) -> str:
    with open(SEARCH_DIRECTORY + "/" + filename, encoding="utf-8") as currentfile:
        # normalise curly apostrophes so "hitchhiker’s" matches "hitchhiker's"
        return currentfile.read().lower().replace("\u2019", "'")


def tokenize(text: str) -> list:
    return WORD_PATTERN.findall(text.lower().replace("\u2019", "'"))


# function for whole-word / whole-phrase matching
def string_match(token: str):
    search_results = {}
    # match the term only when it is not part of a longer word,
    # so "art" does not count inside "party"
    term = re.escape(token.lower().replace("\u2019", "'"))
    pattern = re.compile(r"(?<![a-z0-9])(?<![a-z0-9]')" + term + r"(?!'?[a-z0-9])")
    for filename in listdir(SEARCH_DIRECTORY):
        text = read_document(filename)
        search_results[filename] = len(pattern.findall(text))

    return search_results


# function to use text search using regex
def regex_match(regex: str):
    # print("in regex")
    search_results = {}
    for filename in listdir(SEARCH_DIRECTORY):
        token_count = 0
        text = read_document(filename)
        token_count = len(re.findall(regex, text, re.IGNORECASE))
        search_results[filename] = token_count

    return(search_results)


# function to preprocess content and then search index
def indexed_search(token: str):

    # print("in index search")
    search_results = {}
    search_index = {}

    # preprocess and create a search index
    for filename in listdir(SEARCH_DIRECTORY):
        glossary = {}
        for word in tokenize(read_document(filename)):
            glossary[word] = glossary.get(word, 0) + 1
        search_index[filename] = glossary

    # the index holds single words, so normalise the search term the same way
    terms = tokenize(token)
    for filename, index in search_index.items():
        search_results[filename] = index.get(terms[0], 0) if len(terms) == 1 else 0
    return search_results


def print_results(output: str):
    [
        print(key, "------>", value, "matches")
        for (key, value) in sorted(output.items(), key=lambda x: x[1], reverse=True)
    ]


def main():

    search_method = int(
        input(
            "Choose a search method: 1. String Match 2. Regular Expression 3. Indexed : "
        )
    )

    if search_method not in [1, 2, 3]:
        sys.exit("Please enter a valid input")

    search_token = input("Enter your search string: ")

    token_matches = []
    
    if search_method == 1:
        token_matches = string_match(search_token)
    elif search_method == 2:
        token_matches = regex_match(search_token)
    elif search_method == 3:
        token_matches = indexed_search(search_token)
    else:
        print("Not a valid input, please enter one the options")

    print_results(token_matches)

if __name__ == "__main__":
    # 2. Time for operation
    start_time = time.time()
    main()
    print("Elapsed time: ", (time.time()- start_time))
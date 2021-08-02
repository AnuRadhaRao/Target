import time
import re
import sys
from os import listdir

# path to directory
SEARCH_FILES = "sample_text"


# function for single string matching
def string_match(token: str):
    # print("in string match")
    search_results = {}
    # if token.isalnum() is False:
    #     sys.exit("That is so spaced out")
    for filename in listdir(SEARCH_FILES):
        token_count = 0
        with open(SEARCH_FILES + "/" + filename) as currentfile:
            # print(filename)
            text = currentfile.read().lower()
            # print(text)
            token_count = text.count(token.lower())
            # print(token, " : ", token_count)
        search_results[filename] = token_count
        # print(search_results)

    return(search_results)


# function to use text search using regex
def regex_match(regex: str):
    # print("in regex")
    search_results = {}
    for filename in listdir(SEARCH_FILES):
        token_count = 0
        with open(SEARCH_FILES + "/" + filename) as currentfile:
            # print(filename)
            text = currentfile.read().lower()
            # print(re.findall(regex, text))
            token_count = len(re.findall(regex, text))
        search_results[filename] = token_count

    return(search_results)


# function to preprocess content and then search index
def indexed_search(token: str):

    # print("in index search")
    search_results = {}
    search_index = {}

    # preprocess and create a search index
    for filename in listdir(SEARCH_FILES):
        glossary = {}
        with open(SEARCH_FILES + "/" + filename) as currentfile:
            # text = currentfile.read()
            for line in currentfile:
                line = line.strip()
                line = line.lower()
                words = line.split(" ")
                for word in words:
                    word = [character for character in word if character.isalnum()]
                    word = "".join(word).lower()
                    # print(word)
                    if word not in glossary:
                        glossary[word] = 1
                    else:
                        glossary[word] = glossary.get(word) + 1
            # print(glossary)
        search_index[filename] = glossary
        # print(search_index)

    for filename, index in search_index.items():
        # print(file)
        search_results[filename] = index.get(token.lower(), 0)
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
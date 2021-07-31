# Target Case study - Document Search


Program searches for a set of documents for a phrase or term and returns the results in order of relevance

**Relevance** : Number of times the term or phrase appears in the document

## Description:

User can choose from three methods:
1. **String match** : This function returns an exact return of the match of the token input by the user
2. **Regular expression** : The user inputs the regular expression against which the files are matched and the count of any relevant matches are returned
3. **Indexed** : The token is matched against a preprocessed index and the number of matches are returned

## Usage : 

```
python search_token.py
```
Input the option you wish to use
```
Choose a search method: 1. String Match 2. Regular Expression 3. Indexed : 
```

Enter the search token
```
Enter your search string:
```

## Output:
- The file names and their relevant matches
- The execution time of the program


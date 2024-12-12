# Retrieving data
from whoosh.qparser import QueryParser
from whoosh.index import open_dir

# Index laden
indexDir = "../crawling/indexdir"  # Directory where word index is stored
index = open_dir(indexDir)


while True:
    search_word = input("Enter the word to search for: ")
    with index.searcher() as searcher:
        query = QueryParser("word", index.schema).parse(search_word)
        results = searcher.search(query)
        if len(results) == 0:
            print("No results found.")
            continue
        for result in results:
            print(f"Word: {result['word']}, URL: {result['url']}")

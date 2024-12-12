# Retrieving data
from whoosh.qparser import QueryParser


# Index laden
indexDir = "../crawling/indexDir"  # Directory where word index is stored
index = open_dir(indexDir)


with index.searcher() as searcher:
    # find entries with the words 'first' AND 'last'
    query = QueryParser("content", index.schema).parse("platypus the sole")
    results = searcher.search(query)
    # print all results
    for r in results:
        print(r, "IT DID WORK")

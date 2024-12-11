from whoosh.index import create_in
from whoosh.fields import *
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

from calendar import c
# Define the schema of the index
schema = Schema(word=TEXT(stored=True), url=TEXT)

# Create an index in the directory indexdr (the directory must already exist!)
index = create_in("indexdir", schema)
writer = index.writer()

prefix = "https://vm009.rz.uos.de"
startURL = "https://vm009.rz.uos.de/crawl/index.html"

to_crawl = [startURL]
already_crawled = []
while to_crawl:
    print("To crawl: " + to_crawl.__str__())
    url = to_crawl.pop(0)
    print("Crawling: " + url)
    # get the content of the url
    request = requests.get(url)
    print(request, request.encoding, request.status_code)
    if request.status_code != 200:
            print(f"Skipping {url}: status code {request.status_code}")
            continue

    # parse the content
    soup = BeautifulSoup(request.content, 'html.parser')
    # add the content to the index
    text = soup.get_text()
    words = text.split()
    print(words)
    for word in words:
        writer.add_document(word=word, url=url)

    # Add new links to the to_crawl list
    for link in soup.find_all('a', href=True):
        absLink = urljoin(url, link['href'])

        if absLink not in already_crawled and absLink not in to_crawl and absLink.startswith(prefix):
            to_crawl.append(absLink)
            already_crawled.append(absLink)


# write the index to the disk
writer.commit()

# Retrieving data
from whoosh.qparser import QueryParser
with index.searcher() as searcher:
    # find entries with the words 'first' AND 'last'
    query = QueryParser("content", index.schema).parse("platypus the sole")
    results = searcher.search(query)
    # print all results
    for r in results:
        print(r, "IT DID WORK")

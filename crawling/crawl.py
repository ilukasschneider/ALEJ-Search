from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

# define the schema of the index
schema = Schema(word=TEXT(stored=True), url=TEXT(stored=True))

# create an index in the directory indexdir
index = create_in("indexdir", schema)
writer = index.writer()

# prefix for the URLs to be crawled
prefix = "https://de.wikipedia.org"
# starting URL for the crawler
startURL = "https://de.wikipedia.org/wiki/Osnabrück"


to_crawl = [startURL]
already_crawled = []
# Counter to limit the number of pages to crawl
counter = 10

while to_crawl and counter > 0:
    counter -= 1
    print("To crawl: " + to_crawl.__str__())
    url = to_crawl.pop(0)
    print("Crawling: " + url)

    # get the content of the URL
    request = requests.get(url)
    print(request, request.encoding, request.status_code)
    if request.status_code != 200:
        print(f"skipping {url}: status code {request.status_code}")
        continue

    # parse the content using BeautifulSoup
    soup = BeautifulSoup(request.content, 'html.parser')
    # extract text from the parsed content
    text = soup.get_text()
    words = text.split()
    print(words)

    # add each word to the index
    for word in words:
        writer.add_document(word=word, url=url)

    # add new links to the to_crawl list
    for link in soup.find_all('a', href=True):
        absLink = urljoin(url, link['href'])
        if absLink not in already_crawled and absLink not in to_crawl and absLink.startswith(prefix):
            to_crawl.append(absLink)
            already_crawled.append(absLink)


# Write the index to the disk
writer.commit()

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import defaultdict
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
import os

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk


nltk.download('stopwords')


def create_dirs(word_index_dir, metadata_index_dir):
    if not os.path.exists(word_index_dir):
        os.mkdir(word_index_dir)

    if not os.path.exists(metadata_index_dir):
        os.mkdir(metadata_index_dir)


def create_whoosh_writers(word_index_dir, metadata_index_dir):

    word_schema = Schema(word=TEXT(stored=True), urls=TEXT(stored=True))
    metadata_schema = Schema(url=ID(stored=True, unique=True), title=TEXT(stored=True),
                             headline=TEXT(stored=True), preview=TEXT(stored=True))

    
    word_ix = create_in(word_index_dir, word_schema)
    metadata_ix = create_in(metadata_index_dir, metadata_schema)

    return word_ix.writer(),  metadata_ix.writer()


def extract_metadata(soup):
    title = soup.title.string if soup.title else "No Title"
    headline = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No Headline"
    
    relevant_tags = {"p", "pre", "article", "section", "div"} 

    preview = ""
    for element in soup.body.descendants:
        if element.name in relevant_tags:
            preview = element.get_text(strip=True)
            if preview: 
                break

    # If no relevant tag is found, use raw text excluding overhead
    if not preview:
        raw_text = soup.get_text(strip=True)
        if title in raw_text:
            raw_text = raw_text.replace(title, "")
        if headline in raw_text:
            raw_text = raw_text.replace(headline, "")
        preview = raw_text[:300] 

    preview = preview.strip()[:300]
    return title, headline, preview


def process_text(soup, word_map, url):

    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()

    raw_text = soup.get_text()
    tokenized_text = nltk.word_tokenize(raw_text.lower())
    for word in tokenized_text:
        if word.isalpha() and word not in stop_words:
            stemmed_word = stemmer.stem(word)
            if stemmed_word not in word_map:
                word_map[stemmed_word] = set()
            word_map[stemmed_word].add(url)


def crawl_and_index_meta(start_url, scope_prefix, word_index_dir="word_index", metadata_index_dir="metadata_index"):

    create_dirs(word_index_dir, metadata_index_dir)

    word_writer, metadata_writer = create_whoosh_writers(word_index_dir, metadata_index_dir)

    queue, visited, word_map = [start_url], set(), {}

    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url)
            response.raise_for_status() # important for the 404 page
            soup = BeautifulSoup(response.text, "html.parser")
        except (requests.RequestException, Exception) as e:
            print(f"Error fetching {url}: {e}")
            continue
       
        title, headline, preview = extract_metadata(soup)
        metadata_writer.add_document(url=url, title=title, headline=headline, preview=preview)

        process_text(soup, word_map, url)

        # Add links to the queue
        for link in soup.find_all("a", href=True):
            absolute_url = urljoin(url, link['href'])
            if absolute_url.startswith(scope_prefix) and absolute_url not in visited:
                queue.append(absolute_url)


    for word, urls in word_map.items():
        print(word, urls)
        word_writer.add_document(word=word, urls=";".join(urls))

    word_writer.commit()
    metadata_writer.commit()

    print("Crawling and indexing completed!")


def main():
    start_url = "https://vm009.rz.uos.de/crawl/index.html"
    scope_prefix = "https://vm009.rz.uos.de"

    print("Crawling and indexing, please wait...")

    crawl_and_index_meta(start_url, scope_prefix)

    print("Indexing complete!")

if __name__ == "__main__":
    main()

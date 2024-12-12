import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import defaultdict
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
import os
from whoosh.index import open_dir
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk



nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# this crawler will crawl the web page starting from the start_url and index the words and metadata
# the word index is used to store the words and the urls where they appear
# the metadata index is used to store the title, headline and preview of the page so that it can be displayed in the search results

URL = "https://en.wikipedia.org/wiki/Emmanuel_Macron"
PREFIX = "https://en.wikipedia.org/wiki"
CRAWL_LIMIT = 100


# create directories for saving the indexes
def create_dirs(word_index_dir, metadata_index_dir):
    if not os.path.exists(word_index_dir):
        os.mkdir(word_index_dir)

    if not os.path.exists(metadata_index_dir):
        os.mkdir(metadata_index_dir)

# create whoosh writers for the indexes
def create_whoosh_writers(word_index_dir, metadata_index_dir):

    word_schema = Schema(word=TEXT(stored=True), urls=TEXT(stored=True))
    metadata_schema = Schema(url=ID(stored=True, unique=True), title=TEXT(stored=True),
                             headline=TEXT(stored=True), preview=TEXT(stored=True))


    word_ix = create_in(word_index_dir, word_schema)
    metadata_ix = create_in(metadata_index_dir, metadata_schema)

    return word_ix.writer(),  metadata_ix.writer()


def extract_metadata(soup):

    title = soup.title.get_text(strip=True) if soup.title else "No Title"
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

    # EDIT: Added lemmatization instead of stemming for better resuslts
    # Stemming can create non-existing words, whereas lemmatization returns the base or dictionary form of a word
    lemmatizer = WordNetLemmatizer()

    raw_text = soup.get_text()
    tokenized_text = nltk.word_tokenize(raw_text.lower())
    for word in tokenized_text:
        if word.isalpha() and word not in stop_words:
            lemmatized_word = lemmatizer.lemmatize(word)
            if lemmatized_word not in word_map:
                word_map[lemmatized_word] = set()
            word_map[lemmatized_word].add(url)


def crawl_and_index_meta(start_url = URL, scope_prefix = PREFIX, crawl_limit = CRAWL_LIMIT, word_index_dir="word_index", metadata_index_dir="metadata_index"):

    create_dirs(word_index_dir, metadata_index_dir)

    word_writer, metadata_writer = create_whoosh_writers(word_index_dir, metadata_index_dir)

    queue, visited, word_map = [start_url], set(), {}

    while queue and len(visited) < crawl_limit:
        url = queue.pop(0)
        if url in visited:
            continue
        crawl_limit = crawl_limit - 1
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


# writes the indexes to text files for debugging
def dump_index_to_text(index_dir, output_file):
    index = open_dir(index_dir)
    with index.searcher() as searcher, open(output_file, "w", encoding="utf-8") as f:
        reader = searcher.reader()
        for entry, fields in enumerate(reader.all_stored_fields()):
            f.write(f"Document {entry}:\n")
            for fieldname, value in fields.items():
                f.write(f"{fieldname}: {value}\n")
            f.write("\n")
    print(f"Index from {index_dir} dumped to {output_file}")


def main():

    print("Crawling and indexing, please wait...")

    crawl_and_index_meta()

    # writes the indexes to text files for debugging
    dump_index_to_text("word_index", "debugging/word_index.txt")
    dump_index_to_text("metadata_index", "debugging/metadata_index.txt")

    print("Indexing complete!")

if __name__ == "__main__":
    main()

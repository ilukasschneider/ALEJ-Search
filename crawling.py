from crawler import Crawler
from index import Index
from whoosh.index import open_dir
import sys
# increase the recursion limit to be able to crawl bigger pages
sys.setrecursionlimit(10000)


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

# creates a new Crawler object and provides it with a start url
def initialize_crawler(start_url):
    index = Index()
    crawler = Crawler(index)
    crawler.initialize_crawler(start_url)



def search(query):
    index = Index()  # Assuming the index is already saved; otherwise, persist it between runs
    urls = index.search(query)


if __name__ == "__main__":

    #start_url = input("Enter the start URL: ")
    start_url = "https://fs-cogsci.uos.de"

    initialize_crawler(start_url)
    # uncomment if you want to see the content of the index
    # dump_index_to_text("indexdir", "test.txt")



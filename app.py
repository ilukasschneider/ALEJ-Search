from crawler import Crawler
from index import Index
from whoosh.index import open_dir


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


def initialize_crawler(start_url):
    index = Index()
    crawler = Crawler(index)
    crawler.initialize_crawler(start_url)
    dump_index_to_text("indexdir", "test.txt")



def search(query):
    index = Index()  # Assuming the index is already saved; otherwise, persist it between runs
    urls = index.search(query)
    print("Search results:")
    for url in urls:
        print(url)


if __name__ == "__main__":
    choice = input("Enter 'c' to crawl or 's' to search: ")

    if choice == 'c':
        #start_url = input("Enter the start URL: ")
        start_url = "https://vm009.rz.uos.de/crawl/index.html"

        initialize_crawler(start_url)
    elif choice == 's':
        query = input("Enter your search query: ")
        search(query)
    else:
        print("Invalid choice! Please enter 'c' or 's'.")


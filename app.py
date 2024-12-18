from crawler import Crawler
from index import Index

def initialize_crawler(start_url):
    index = Index()
    crawler = Crawler(index)
    crawler.initialize_crawler(start_url)

def search(query):
    index = Index()  # Assuming the index is already saved; otherwise, persist it between runs
    urls = index.search(query)
    print("Search results:")
    for url in urls:
        print(url)

if __name__ == "__main__":
    choice = input("Enter 'c' to crawl or 's' to search: ")

    if choice == 'c':
        start_url = input("Enter the start URL: ")
        initialize_crawler(start_url)
    elif choice == 's':
        query = input("Enter your search query: ")
        search(query)
    else:
        print("Invalid choice! Please enter 'c' or 's'.")
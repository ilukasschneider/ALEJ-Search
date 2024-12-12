import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse



class Crawler:
    def __init__(self, index):
        self.to_visit = []
        self.visited = set()
        self.index = index
        self.base_domain = None


    def initialize_crawler(self, start_url):
        self.base_domain = urlparse(start_url).netloc
        self.to_visit.append(start_url)
        self.crawl()


    def crawl(self):
        while self.to_visit:
            current_url = self.to_visit.pop(0)
            self.visited.add(current_url)
            self.process(current_url)
            self.parse(current_url)


    # make sure we do not switch the domain
    def is_same_domain(self, link, base_url):
        # Resolve full URL and extract its domain
        full_url = urljoin(base_url, link)
        link_domain = urlparse(full_url).netloc
        return link_domain == self.base_domain

    # search for other urls in the current url and append them
    def process(self, url):
        # get the other urls
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        self.to_visit.extend(
            [
                urljoin(url, link['href'])
                for link in links
                # check if it is the same domain
                if self.is_same_domain(link['href'], url) and
                    # make sure it is a new link
                   urljoin(url, link['href']) not in self.visited and
                   urljoin(url, link['href']) not in self.to_visit
            ]
        )

    # pass url and text to the index
    def parse(self, url):
        try:
            # get the content of the page
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)

            # pass url and text to the index
            self.index.index_content(url, text)
            return [a['href'] for a in soup.find_all('a', href=True)]
        except Exception as e:
            print(f"Failed to parse {url}: {e}")
            return []
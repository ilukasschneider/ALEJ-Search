import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import traceback
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from tokenizer import *

import nltk

nltk.download("wordnet")
nltk.download("omw-1.4")


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
            soup = self.process(current_url)
            if soup:
                self.parse(current_url, soup)


    # make sure we do not switch the domain
    def is_same_domain(self, link, base_url):
        # Resolve full URL and extract its domain
        full_url = urljoin(base_url, link)
        link_domain = urlparse(full_url).netloc
        return link_domain == self.base_domain

    # search for other urls in the current url and append them
    def process(self, url):
        # get the other urls
        try:
            response = requests.get(url)
            response.raise_for_status()
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
            return soup
        except Exception as e:
            print("404 found. ", e)
            return None

    def extract_metadata(self, soup):
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


   

    # pass url and text to the index
    def parse(self, url, soup):

        try:
            # get the content of the page

            text = soup.get_text(separator=' ', strip=True)
            text = process_text(text)
            
            title, headline, preview = self.extract_metadata(soup)


            # pass url and text to the index
            self.index.index_content(url, text, title, headline, preview)
            
        except Exception as e:
            traceback.print_exc()
            print(f"Failed to parse {url}: {e}")
            
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

        # pagerank data
        self.out_count = {} # url: count of outgoing links
        self.in_urls = {} # url: set of url linking to this url


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
        
        self.pagerank()

    # if an url is not in out_count is hasnt been crawled (e.g. 404) -> this would mess up ranking propagation so remove from in_urls
    def clean_pr_data(self):
        for url in list(self.in_urls.keys()):
            if url not in self.out_count:
              
                for in_url in self.in_urls[url]: self.out_count[in_url] -= 1

                del self.in_urls[url]


    def calculate_score(self, pr, url):
        score = 0 
        for in_url in self.in_urls[url]:
            if in_url in self.out_count and self.out_count[in_url] > 0: 
                score += pr[in_url] / self.out_count[in_url]
        return score


    def pagerank(self):
        max_iterations = 1000
        tolerance = 1e-6
        self.clean_pr_data()
        
        pr = {key: 1/len(self.out_count) for key in self.out_count}

        for i in range(max_iterations):
            next_pr = {}
            for url in pr.keys():  
                next_pr[url] = self.calculate_score(pr, url)


            max_change = max(abs(next_pr[url] - pr[url]) for url in pr.keys())
            pr = next_pr

            if max_change < tolerance:
                print(f"Converged after {i + 1} iterations.")
                break

        print(pr)
        self.index.add_pr(pr)
        

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
           
            rel_out = [urljoin(url, link['href']) for link in links if self.is_same_domain(link['href'], url)]
            
            self.out_count[url] = len(rel_out)
            
            for out in rel_out:
                if out in self.in_urls:
                    self.in_urls[out].add(url)
                else:
                    self.in_urls[out] = {url}
                    self.out_count
            
           
            self.to_visit.extend(
                [
                    link
                    for link in rel_out
                     # make sure it is a new link
                    if link not in self.visited and
                    link not in self.to_visit
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
            
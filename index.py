import os
import requests
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from tokenizer import *


class Index:
    def __init__(self):
        self.index_dir = "indexdir"
        self.schema = Schema(url=ID(stored=True, unique=True), content=TEXT(stored=True), title=TEXT(stored=True), headline=TEXT(stored=True), preview=TEXT(stored=True))
        self.ix = self.create_or_open_index()

    # check if there is already a file, create one if not
    def create_or_open_index(self):
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
            return index.create_in(self.index_dir, self.schema)
        return index.open_dir(self.index_dir)


    # add the url and its respective text to the index
    def index_content(self, url, text, title, headline, preview):
        writer = self.ix.writer()
        try:
            writer.add_document(url=url, content=text, title=title, headline=headline, preview=preview)
        except Exception as e:
            print(f"Failed to index content from {url}: {e}")
        finally:
            writer.commit()


    # search in the index for the query
    def search(self, query_str):
        with self.ix.searcher() as searcher:
            query_str = process_text(query_str)

            query = QueryParser("content", self.ix.schema).parse(query_str)

            results = searcher.search(query)

            # return the urls in a list, list is empty if no url is found
            unique_urls = set()
            result_urls = []
            for result in results:
                if result["url"] not in unique_urls:
                    unique_urls.add(result["url"])
                    res_dict = {"url": result['url'], "title": result["title"], "headline": result["headline"], "preview": result["preview"]}
                    result_urls.append(res_dict)
                    print("URL:", result['url'], result["title"])
            return result_urls  # Always return a list, even if empty
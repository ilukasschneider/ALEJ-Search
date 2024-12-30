import os
import requests
from whoosh import index, sorting
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser
from tokenizer import *


class Index:
    def __init__(self):
        self.index_dir = "indexdir"
        self.schema = Schema(url=ID(stored=True, unique=True), content=TEXT(stored=True), title=TEXT(stored=True), headline=TEXT(stored=True), preview=TEXT(stored=True))#, pagerank=NUMERIC(stored=True, sortable=True))
        self.ix = self.create_or_open_index()

    # check if there is already a file, create one if not
    def create_or_open_index(self):
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
            return index.create_in(self.index_dir, self.schema)
        return index.open_dir(self.index_dir)


    # add the url and its respective text to the index
    def index_content(self, url, text, title, headline, preview):
        print("in index_content")
        writer = self.ix.writer()
        print("we wrote")
        try:
            print("before add")
            #print(url, text, title, headline, preview)
            writer.add_document(url=url, content=text, title=title, headline=headline, preview=preview)

            print("we added")
            # with self.ix.searcher() as searcher:
            #     existing_doc = searcher.document(url=url)
            #
            # if existing_doc:
            #     # If the document exists, update it
            #     print(f"Document with URL {url} exists, updating...")
            #     writer.update_document(url=url, title=title, headline=headline, preview=preview)
            #     print("after updateeeeeee")
            # else:
            #     # If the document does not exist, add it
            #     print(f"Document with URL {url} does not exist, adding it...")
            #     writer.add_document(url=url, content=text, title=title, headline=headline, preview=preview)
            #
            #
            # #writer.update_document(url=url, title=title)#, headline=headline, preview=preview)
            # print("after update")
        except Exception as e:
            print(f"Failed to index content from {url}: {e}")
        finally:
            writer.commit()
            print("in finally")


    def add_pr(self, pr):
        with self.ix.searcher() as searcher:  
            with self.ix.writer() as writer:  
                for url, score in pr.items():
                    existing_doc = searcher.document(url=url)
                    if existing_doc:
                        # Needs to be done this way, otherwise will overwrite the other fields.. 
                        writer.update_document(
                            url=url,
                            content=existing_doc.get("content"),
                            title=existing_doc.get("title"),
                            headline=existing_doc.get("headline"),
                            preview=existing_doc.get("preview"),
                            pagerank=score 
                        )
                    else:
                        print(f"Document with URL {url} not found. Skipping.")
               

    # search in the index for the query
    def search(self, query_str):
        with self.ix.searcher() as searcher:
            query_str = process_text(query_str)

            query = QueryParser("content", self.ix.schema).parse(query_str)

            
            results = searcher.search(query, sortedby="pagerank") # the sorting does not work for some reason
    
            unique_urls = set()
            result_urls = []
            for result in results:
                if result["url"] not in unique_urls:
                    unique_urls.add(result["url"])
                    res_dict = {"url": result['url'], "title": result["title"], "headline": result["headline"], "preview": result["preview"]}#, "pagerank": result["pagerank"]}
                    result_urls.append(res_dict)
                    print("URL:", result['url'], result["title"])#, result["pagerank"])
            
            #result_urls.sort(key=lambda x: x["pagerank"], reverse=True) # sort by pagerank
            print(result_urls)
            return result_urls 
# File contains Index class to manage all the index related tasks (search, saving to disk, ..)
import os
import requests
from whoosh import index, sorting
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser
from tokenizer import *


class Index:
    def __init__(self):
        self.index_dir = "indexdir"
        # store url with a couple of additional information about each page 
        self.schema = Schema(url=ID(stored=True, unique=True), content=TEXT(stored=True), title=TEXT(stored=True), headline=TEXT(stored=True), preview=TEXT(stored=True), pagerank=NUMERIC(stored=True, sortable=True))
        self.ix = self.create_or_open_index()


    def create_or_open_index(self):
        # if there is no index yet create a new directory, otherwise the existing one will be manipulated
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
            return index.create_in(self.index_dir, self.schema)
        return index.open_dir(self.index_dir)


    # add the url and its respective text as well as  to the index
    def index_content(self, url, text, title, headline, preview):

        writer = self.ix.writer()

        try:
            writer.add_document(url=url, content=text, title=title, headline=headline, preview=preview)

        except Exception as e:
            print(f"Failed to index content from {url}: {e}")
        finally:
            writer.commit()


    # adds the pagerank values to the whoosh index
    def add_pr(self, pr):
        with self.ix.searcher() as searcher:  
            with self.ix.writer() as writer:  
                for url, score in pr.items():
                    existing_doc = searcher.document(url=url)
                    if existing_doc:
                       
                        content, title, headline, preview = existing_doc.get("content"), existing_doc.get("title"), existing_doc.get("headline"), existing_doc.get("preview")
                        # Needs to be done this way, otherwise will overwrite the other fields and add a new document even if we use the update function.. for some reason 
                        writer.delete_by_term("url", url)
                        writer.add_document(
                            url=url,
                            content=content ,
                            title=title,
                            headline=headline,
                            preview=preview,
                            pagerank=score 
                        )
                       
                    else:
                        print(f"Document with URL {url} not found. Skipping.")
               

    # search in the index for the query
    def search(self, query_str):
        pr_weight, score_weight = 0.5, 0.5
        with self.ix.searcher() as searcher:
            query_str = process_text(query_str)

            query = QueryParser("content", self.ix.schema).parse(query_str)

            
            results = searcher.search(query) 
    
            unique_urls = set()
            result_urls = []
            max_pr, max_score = 0, 0
            # check the pageranks and sort the results according to them
            for result in results:
               
                if result["pagerank"] > max_pr: max_pr = result["pagerank"]
                if result.score > max_score: max_score = result.score

                print(result.score)
                if result["url"] not in unique_urls:
                    unique_urls.add(result["url"])
                    res_dict = {"url": result['url'], "title": result["title"], "headline": result["headline"], "preview": result["preview"], "pagerank": result["pagerank"], "score": result.score}
                    result_urls.append(res_dict)
            
            # sort s the result by a weighted sum
            # combines the quality of the page (pagerank) with how well the page relates to the query (whoosh score)
            result_urls.sort(key=lambda x:  pr_weight * (x["pagerank"] / max_pr) + score_weight * (x["score"] / max_score), reverse=True) 
            
            return result_urls 
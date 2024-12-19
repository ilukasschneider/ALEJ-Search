from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
from index import Index

# Ensure NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """Render the search form."""
    return render_template("index.html")


def search(query):
    index = Index()  # Assuming the index is already saved; otherwise, persist it between runs
    results = index.search(query)
    print("Search results:")
    for url in results:
        print(url)
    
    return results


@app.route('/results', methods=['POST'])
def results():
    """Handle search queries and display results."""
    user_query = request.form['query']
    original_query = user_query

    
    # query_words = nltk.word_tokenize(user_query.lower())
    # stemmed_words = [stemmer.stem(word) for word in query_words if word.isalpha() and word not in stop_words]
    # search_query = " OR ".join(stemmed_words)

    # Search word index to find matching URLs
    # matching_urls = set()
    # with word_ix.searcher() as word_searcher:
    #     word_query = QueryParser("word", schema=word_ix.schema).parse(search_query)
    #     word_results = word_searcher.search(word_query, limit=None)
    #     for hit in word_results:
    #         matching_urls.update(hit["urls"].split(";"))

    # Fetch metadata for the found URLs
    results = search(user_query)

    # with metadata_ix.searcher() as metadata_searcher:
    #     for url in matching_urls:
    #         metadata_query = QueryParser("url", schema=metadata_ix.schema).parse(f'"{url}"')
    #         metadata_results = metadata_searcher.search(metadata_query)
    #         for meta_hit in metadata_results:
    #             results.append({
    #                 "url": meta_hit["url"],
    #                 "title": meta_hit["title"],
    #                 "headline": meta_hit["headline"],
    #                 "preview": meta_hit["preview"],
    #             })

    return render_template("results.html", results=results, original_query=original_query)

if __name__ == '__main__':
    app.run(debug=True)

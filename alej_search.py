from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Ensure NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')

nltk.download('wordnet')
nltk.download('omw-1.4')

app = Flask(__name__)

# Load indices
word_index_path = "word_index"  # Directory where word index is stored
metadata_index_path = "metadata_index"  # Directory where metadata index is stored
word_ix = open_dir(word_index_path)
metadata_ix = open_dir(metadata_index_path)

# Initialize NLTK tools
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

@app.route('/', methods=['GET'])
def index():
    """Render the search form."""
    return render_template("index.html")

@app.route('/results', methods=['POST'])
def results():
    """Handle search queries and display results."""
    user_query = request.form['query']
    original_query = user_query


    query_words = nltk.word_tokenize(user_query.lower())
    lematized_words = [lemmatizer.lemmatize(word) for word in query_words if word.isalpha() and word not in stop_words]
    search_query = " OR ".join(lematized_words)

    # Search word index to find matching URLs
    matching_urls = set()
    with word_ix.searcher() as word_searcher:
        word_query = QueryParser("word", schema=word_ix.schema).parse(search_query)
        word_results = word_searcher.search(word_query, limit=None)
        for hit in word_results:
            matching_urls.update(hit["urls"].split(";"))

    # Fetch metadata for the found URLs
    results = []
    with metadata_ix.searcher() as metadata_searcher:
        for url in matching_urls:
            metadata_query = QueryParser("url", schema=metadata_ix.schema).parse(f'"{url}"')
            metadata_results = metadata_searcher.search(metadata_query)
            for meta_hit in metadata_results:
                results.append({
                    "url": meta_hit["url"],
                    "title": meta_hit["title"],
                    "headline": meta_hit["headline"],
                    "preview": meta_hit["preview"],
                })

    return render_template("results.html", results=results, original_query=original_query)

if __name__ == '__main__':
    app.run(debug=True)

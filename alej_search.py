from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
from index import Index

# Ensure NLTK resources are downloaded
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

app = Flask(__name__)

RESULTS_PER_PAGE = 2 # modify if you want to change the number of results shown per page


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


@app.route('/results', methods=['GET','POST'])
def results():
    """Handle search queries and display results."""
    if request.method == 'POST':
        # Handle search query submission (POST request)
        user_query = request.form['query']
        original_query = user_query
    else:
        # Handle pagination (GET request)
        user_query = request.args.get('query', '')  # Default to empty string if 'query' is not in the URL
        original_query = user_query

    if not user_query:  # If no query is provided, return an error or default behavior
        return render_template('error.html', message="No search query provided.")

    results = search(user_query)

    # Pagination logic
    page = request.args.get('page', 1, type=int)  # Get current page number from query parameters
    total_results = len(results)
    start = (page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    paginated_results = results[start:end]

    total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE  # Ceiling division
    pagination_info = {
        'current_page': page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1,
        'next_page': page + 1,
    }

    return render_template(
        "results.html",
        results=paginated_results,
        original_query=original_query,
        pagination_info=pagination_info,
        user_query=user_query
    )


if __name__ == '__main__':
    app.run(debug=True)

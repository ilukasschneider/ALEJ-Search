# ALEJ-Search
Task2: Artificial Intelligence and the Web (WiSe 2024/25)

This project is a basic search engine developed as part of an university course task. It uses the Whoosh library for indexing scraped web content and Flask to serve the application as a web interface. The aim is to provide a simple yet effective search engine that demonstrates core principles of web scraping, indexing, and serving content over the web.

## Running the Application

### Prerequisites
Before running the application, install all necessary dependencies:
~~~bash
pip install -r requirements.txt
~~~

### 1. Start the Crawler
Begin by running the crawler to scrape and index web content. This step only needs to be done once so that the search engine has web content to search through:
~~~bash
python crawling.py
~~~

Alternatively, you can use the provided index that was a result from crawling https://fs-cogsci.uos.de/

### 2. Launch the Frontend
Once the crawler has finished, start the Flask web server to serve the frontend:
~~~bash
flask --app alej_search run
~~~

The App is also deployed on a server provided by the University of Osnabrück and can be reached via
http://vm146.rz.uni-osnabrueck.de/u063/alej-search.wsgi/

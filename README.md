# ALEJ-Search
Task2: Artificial Intelligence and the Web (WiSe 2024/25)

## Running the Application

### Prerequisites
Before running the application, install all necessary dependencies:
~~~bash
pip install -r requirements.txt
~~~

### 1. Start the Crawler
Begin by running the crawler to scrape and index web content. This step only needs to be done once so that the search engine has web content to search through:
~~~bash
python crawler.py
~~~

### 2. Launch the Frontend
Once the crawler has finished, start the Flask web server to serve the frontend:
~~~bash
flask --app app run
~~~

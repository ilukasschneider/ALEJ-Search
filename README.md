# ALEJ-Search
 Task2: Artificial Intelligence and the Web (WiSe 2024/25)

# Run:
## First the Crawler
python crawler.py

## When Crawler is finished: Frontend:
flask --app alej_search run


# Concept:
## Crawler:
- Crawls only given Domain (example url)
- Filters Stopwords
- Uses Stemming
- creates two indices:
    - word_index: stores url list for every stemmed word
    - metadata_index: stores title, headline and preview for every url encountered

## Search:
- Stemms search term
- First searches the word_index and lists the urls
- Then searches the metadata_index for infos about urls

# Improvement Ideas

- fix page ranking $\to$ does not work properly?
- fix preview

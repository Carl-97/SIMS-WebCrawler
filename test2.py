from urllib.parse import quote
from ExcelManip import excelmanip as em
from WebCrawler.crawlerDemo5 import WebCrawler
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def find_relevant_content(query, scraped_data, n=3):  # Default top 3, you can adjust as required
    # Combining the query with the scraped data
    all_texts = [query] + scraped_data

    # Create a TF-IDF vectorizer and fit-transform the texts
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Calculate cosine similarity between the query and all scraped content
    cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Get the indices of the top 'n' most similar contents
    top_indices = cosine_sims.argsort()[-n:][::-1]  # We reverse it because argsort returns in ascending order

    return [scraped_data[i] for i in top_indices]


def find_relevant_content_2(query, scraped_data, n=3):
    # Stop words list can be expanded based on domain-specific knowledge
    stop_words = {"and", "the", "is", "in", "for", "of", "or", "on", "with"}

    # TF-IDF vectorizer with some tuning
    vectorizer = TfidfVectorizer(
        stop_words=stop_words,
        ngram_range=(1, 2),  # considering bigrams can capture terms like "PowerDrain V100P/G"
        max_df=0.85,  # ignore terms that appear in more than 85% of the documents
        min_df=0.15  # ignore terms that appear in less than 15% of the documents
    )

    # Combine the query with the scraped data and transform
    all_texts = [query] + scraped_data
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Calculate cosine similarity between the query and scraped content
    cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Get the indices of the top 'n' most similar contents
    top_indices = cosine_sims.argsort()[-n:][::-1]

    # Extract the most relevant pieces of content based on the indices
    relevant_content = [scraped_data[i] for i in top_indices]

    return relevant_content


def process_with_id(id_val, web_crawler, index):
    websites = [
        f'https://www.e-nummersok.se/sok?Query={id_val}',
        f'https://www.rskdatabasen.se/sok?Query={id_val}'
    ]
    for url in websites:
        web_crawler.crawl_website_with_depth(str(index), 0, start_url=url)


def process_without_id(data_dict, web_crawler, index):
    filtered_values = [value for value in data_dict.values() if value is not None]
    if filtered_values:
        search_query = " ".join(filtered_values)
        search_query = quote(search_query)
        google_search_url = f'https://www.google.com/search?q={search_query}'
        web_crawler.crawl_website_with_depth(str(index), 1, start_url=google_search_url)
    else:
        print("Dictionary has no valid values to perform a search.")


if __name__ == '__main__':
    start_time = time.time()
    file_path = 'resources/QualityTest2.xlsx'
    excel = em.ExcelManip(file_path)
    data = excel.pre_process()
    wc = WebCrawler()

    for idx, dictionary in enumerate(data, start=1):
        if 'id' in dictionary and dictionary['id'] is not None:
            id_nr = dictionary['id']
            process_with_id(id_nr, wc, idx)
            process_without_id(dictionary, wc, idx)
        else:
            process_without_id(dictionary, wc, idx)

        # Form the query from the dictionary
        query = " ".join([str(val) for val in dictionary.values() if val is not None])

        # Let's say the content you scraped is stored line-by-line in a CSV file named by the index
        with open(f"temp_files/{idx}.csv", 'r', encoding='utf-8') as f:
            scraped_content = f.readlines()

        # If scraped content is empty, continue to the next iteration
        if not scraped_content:
            print(f"File {idx}.csv is empty. Skipping...")
            continue

        # Get the top 'n' relevant pieces of content
        relevant_pieces = find_relevant_content(query, scraped_content)

        for piece in relevant_pieces:
            print(f'{idx} : {piece}')

    print("------Done------")
    wc.close()
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Execution time: {total_time:.2f} seconds")


from urllib.parse import quote
from ExcelManip import excelmanip as em
from WebCrawler.crawlerDemo5 import WebCrawler
import time


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
        print(f'{google_search_url}')
        web_crawler.crawl_website_with_depth(str(index), 1, start_url=google_search_url)
    else:
        print("Dictionary has no valid values to perform a search.")


if __name__ == '__main__':
    start_time = time.time()
    file_path = 'resources/ifm_10.xlsx'
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

    print("------Done------")
    wc.close()
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Execution time: {total_time:.2f} seconds")

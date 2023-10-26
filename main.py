import os.path
from urllib.parse import quote
from ExcelManip import excelidentify as em
from WebCrawler.crawler import WebCrawler
import postprocess as pp
import time

KEYS = ['brand', 'article_id', 'type_desc']


def crawl_with_keys(data_dict, web_crawler, index):
    values_to_use = [data_dict[key] for key in KEYS if key in data_dict and data_dict[key] is not None]
    if values_to_use:
        print(f'Key Value: {values_to_use}')
        search_query = " ".join(values_to_use)
        search_query = quote(search_query)
        google_search_url = f'https://www.google.com/search?q={search_query}'
        print(f'{google_search_url}')
        web_crawler.crawl_website_with_depth(str(index), 1, start_url=google_search_url)
    else:
        print("Dictionary has no valid values to perform a search.")


def crawl_with_id(id_val, web_crawler, index):
    websites = [
        f'https://www.e-nummersok.se/sok?Query={id_val}',
        f'https://www.rskdatabasen.se/sok?Query={id_val}'
    ]
    for url in websites:
        web_crawler.crawl_website_with_depth(str(index), 0, start_url=url)


def crawl_all(data_dict, web_crawler, index):
    filtered_values = [value for value in data_dict.values() if value is not None]
    if filtered_values:
        search_query = " ".join(filtered_values)
        search_query = quote(search_query)
        google_search_url = f'https://www.google.com/search?q={search_query}'
        #print(f'{google_search_url}')
        web_crawler.crawl_website_with_depth(str(index), 1, start_url=google_search_url)
    else:
        print("Dictionary has no valid values to perform a search.")


def run(file):
    excel = em.ExcelManip(file)
    data = excel.pre_process()
    wc = WebCrawler()

    for idx, dictionary in enumerate(data, start=1):
        if 'id' in dictionary and dictionary['id'] is not None:
            id_nr = dictionary['id']
            crawl_with_id(id_nr, wc, idx)
            crawl_with_keys(dictionary, wc, idx)
        else:
            crawl_with_keys(dictionary, wc, idx)
    wc.close()

    excel_processor = pp.ExcelProcessor(
        input_file=file,
        output_file='result.xlsx',
        csv_directory='temp_files'
    )
    excel_processor.process_excel()


def run_identify(file):
    excel = em.ExcelManip(file)
    data = excel.pre_process()
    return data


def run_crawl(data):
    wc = WebCrawler()
    for idx, dictionary in enumerate(data, start=1):
        if 'id' in dictionary and dictionary['id'] is not None:
            id_nr = dictionary['id']
            crawl_with_id(id_nr, wc, idx)
            crawl_with_keys(dictionary, wc, idx)
        else:
            crawl_with_keys(dictionary, wc, idx)
    wc.close()


def run_postprocess(file):
    excel_processor = pp.ExcelProcessor(
        input_file=file,
        output_file='result.xlsx',
        csv_directory='temp_files'
    )
    excel_processor.process_excel()


def empty_folder(path):
    if os.path.exists(path):
        files = os.listdir(path)
        for file in files:
            target_file = os.path.join(path, file)
            if os.path.isfile(target_file):
                os.remove(target_file)
    else:
        return


if __name__ == '__main__':
    file_path = 'resources/QualityTest.xlsx'
    start_time = time.time()
    empty_folder('temp_files')
    run(file_path)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time: {total_time:.2f} seconds")
    print("------Done------")
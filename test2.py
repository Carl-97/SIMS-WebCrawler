from ExcelManip import excelmanip as em
from WebCrawler.crawlerDemo4 import WebCrawler
from urllib.parse import quote
import os
import openpyxl
from openpyxl.styles import PatternFill

if __name__ == '__main__':
    file_path = 'resources/QualityTest2.xlsx'
    excel = em.ExcelManip(file_path)
    data = excel.pre_process()
    wc = WebCrawler()
    filename = 'data.csv'
    i = 1
    for dictionary in data:
        if 'id' in dictionary and dictionary['id'] is not None:
            id_val = dictionary['id']
            e_nr_url = f'https://www.e-nummersok.se/sok?Query={id_val}'
            rsk_nr_url = f'https://www.rskdatabasen.se/sok?Query={id_val}'
            wc.crawl_website_with_depth(str(i), 0, start_url=e_nr_url)
            wc.crawl_website_with_depth(str(i), 0, start_url=rsk_nr_url)
        else:
            #print("No 'id' found. Performing a Google search...")
            # Filter out None values from the dictionary's values
            filtered_values = [value for value in dictionary.values() if value is not None]
            if filtered_values:
                # Construct a Google search query using the filtered values
                search_query = " ".join(filtered_values)
                search_query = quote(search_query)  # URL encode the search query
                google_search_url = f'https://www.google.com/search?q={search_query}'
                print(f'Search Query {i}: {google_search_url}')
                wc.crawl_website_with_depth(str(i), 1, start_url=google_search_url)
            else:
                print("Dictionary has no valid values to perform a search.")
        i += 1
    print("------Done------")
    wc.close()
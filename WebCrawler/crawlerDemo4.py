import time
import os
import csv
import queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse


class WebCrawler:
    def __init__(self):
        self.driver = self.setup_headless_chrome()
        self.link_queue = queue.Queue()
        self.visited = set()
        self.ignore_list = self.set_ignorelist_url()

    @staticmethod
    def setup_headless_chrome():
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--enable-javascript')
        # check about 'download restrictions' and its features
        chrome_options.add_argument('--disable-features=BlockThirdPartyCookies,DownloadRestrictions')
        return webdriver.Chrome(options=chrome_options)

    def get_html_content(self, url):
        try:
            self.driver.get(url)
            # Wait for the page to fully load (handle redirections)
            time.sleep(3)
            wait = WebDriverWait(self.driver, 2)
            wait.until(ec.presence_of_element_located((By.TAG_NAME, 'body')))
            return self.driver.page_source
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    @staticmethod
    def has_product(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return bool(soup.select('div[class*="product"]')) or bool(soup.select('div[id*="product"]'))

    @staticmethod
    def is_pdf(url):
        # checks if its end with .pdf
        return url.lower().endswith('.pdf')

    def clean_html_content(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        # add class names you want to remove
        classes_to_remove = ['header', 'footer', 'nav', 'navbar']
        #ignorecontent
        for class_name in classes_to_remove:
            elements_with_class = soup.find_all(class_name)
            for element in elements_with_class:
                self.remove_all_children(element)
        for class_name in classes_to_remove:
            elements_with_class = soup.find_all(div_=class_name)
            for element in elements_with_class:
                self.remove_all_children(element)

        return soup.body.get_text()

    @staticmethod
    def remove_all_children(element):
        for child in element.find_all(recursive=False):
            if isinstance(child, Tag):
                child.decompose()

    @staticmethod
    def find_valid_links(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a', href=True) if WebCrawler.is_valid_link(link.get('href'))]
        return links

    @staticmethod
    def is_valid_link(url):
        # Add more file extensions if found
        excluded_extensions = ['.pdf', '.jpg', '.png', '.gif', '.zip', '.mp3', '.mp4']

        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        #can be added for further development
        # path = parsed_url.path
        lower_url = url.lower()

        # Check if the scheme is 'http' or 'https'
        # Check if the netloc (domain) is present
        # Exclude links with specific file extensions
        is_http_or_https = scheme in ['http', 'https']
        is_valid_netloc = bool(netloc)
        has_valid_extension = not any(lower_url.endswith(ext) for ext in excluded_extensions)

        return is_http_or_https and is_valid_netloc and has_valid_extension

    @staticmethod
    def save_content_to_csv(content, csv_filename):
        # Add folder for saved files
        folder_path = 'temp_files'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Check if the filename ends with ".csv" and add it if not
        if not csv_filename.endswith('.csv'):
            csv_filename += '.csv'

        file_path = f'temp_files/{csv_filename}'
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        mode = 'a' if os.path.exists(file_path) else 'w'
        with open(file_path, mode, newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows([[line] for line in lines])

    @staticmethod
    def set_ignorelist_url():
        with open("resources/ignoreUrls.csv", mode='r') as file:
            csv_reader = csv.reader(file)
            array=[]
            for row in csv_reader:
               # decode_row = [cell.decode('utf-8') for cell in row]
                array.append(row[0])
        return array

    def is_search_engine_url(self, url):
        # Define a list of known search engine domains (you can add more if needed)
        #string_array = self.ignorelist
        #binary_data = [s.encode('utf-8') for s in string_array]
        #search_engine_domains =  binary_data
        search_engine_domains = self.ignore_list

        parsed_url = urlparse(url)
        netloc = parsed_url.netloc

        #netloc =
        # Check if the netloc (domain) of the URL is in the list of search engine domains
        return any(search_engine_domain in netloc for search_engine_domain in search_engine_domains)

    @staticmethod
    def extract_search_engine_links(html_content):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Find the specific div element by its id ("search")
            search_div = soup.find('div', id='search')

            # Initialize a list to store the extracted links
            search_result_links = []
    
            # Check if the div element with the specified id was found
            if search_div:
                # Extract links from the div element, assuming links are in <a> tags
                links = search_div.find_all('a', href=True)
                search_result_links = [link['href'] for link in links]
                return search_result_links
            return search_result_links
        except Exception as e:
            print(f"Error parsing HTML content: {e}")
            return ""

    def crawl_website_with_depth(self, csv_filename, depth_limit, start_url):
        self.link_queue.put((start_url, 0))
        separator = '-' * 40
        while not self.link_queue.empty():
            current_url, current_depth = self.link_queue.get()

            # Check if the current URL is from a search engine and skip scraping if true
            print(current_url)
            if self.is_search_engine_url(current_url):
                print(f"Skipping scraping for search engine URL: {current_url}")
                if current_depth == 0:
                    html_content = self.get_html_content(current_url)
                    valid_links = self.extract_search_engine_links(html_content)
                    time.sleep(2)
                    for link in valid_links[:5]:
                        self.link_queue.put((link, current_depth + 1))
            else:
                if current_depth > depth_limit or current_url in self.visited:
                    continue
                self.visited.add(current_url)
                html_content = self.get_html_content(current_url)
                time.sleep(2)
                if not html_content:
                    continue
                #scraped_url = self.driver.current_url
                if self.is_valid_link(current_url):
                    cleaned_content = self.clean_html_content(html_content)
                    cleaned_content = current_url + '\n' + cleaned_content + '\n' + separator
                    self.save_content_to_csv(cleaned_content, csv_filename)
                elif '.pdf' in current_url:
                    cleaned_content = current_url + '\n' + separator
                    self.save_content_to_csv(cleaned_content, csv_filename)

                # Add valid links to the queue regardless of whether it's a search engine URL
                for link in self.find_valid_links(html_content):
                    self.link_queue.put((link, current_depth + 1))

    def close(self):
        self.driver.quit()


# Testing the web crawler
if __name__ == '__main__':
    crawler = WebCrawler()
    test_url = 'https://www.e-nummersok.se/lista/plintsystem-plint-och-kabelmarkning-apparats/plintsystem-for-skenmontage/weidmuller/plint-sakr-pa-m-2920154-14020'
    crawler.crawl_website_with_depth('test_file.csv', 1, test_url)
    crawler.close()

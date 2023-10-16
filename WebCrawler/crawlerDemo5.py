import time
import os
import csv
import queue
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse


class WebCrawler:
    _max_retries = 3  # Maximum number of retries
    _retry_delay = 3  # Number of seconds to wait between retries

    def __init__(self):
        self.driver = self.setup_headless_chrome()
        self.link_queue = queue.Queue()
        self.visited = set()
        self.ignore_list = self.set_ignorelist_url()

    @staticmethod
    def set_ignorelist_url():
        with open("resources/ignoreUrls.csv", mode='r') as file:
            csv_reader = csv.reader(file)
            array=[]
            for row in csv_reader:
               # decode_row = [cell.decode('utf-8') for cell in row]
                array.append(row[0])
        return array

    @staticmethod
    def setup_headless_chrome():
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--enable-javascript')
        # check about 'download restrictions' and its features
        chrome_options.add_argument('--disable-features=BlockThirdPartyCookies,DownloadRestrictions')
        return webdriver.Chrome(options=chrome_options)

    def get_html_content(self, url):
        for retry in range(self._max_retries):
            try:
                self.driver.get(url)
                # Wait for the page to fully load (handle redirections)
                time.sleep(3)
                wait = WebDriverWait(self.driver, 2)
                wait.until(ec.presence_of_element_located((By.TAG_NAME, 'body')))
                return self.driver.page_source
            except WebDriverException as e:
                print(f"Error fetching {url} (Attempt {retry + 1}/{self._max_retries}): {e}")
                if retry < self._max_retries - 1:
                    print(f"Retrying in {self._retry_delay} seconds...")
                    time.sleep(self._retry_delay)
        print(f"Max retries reached for {url}. Unable to fetch content.")
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
        # ignorecontent
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

        file_path = f'{folder_path}/{csv_filename}'
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        mode = 'a' if os.path.exists(file_path) else 'w'
        with open(file_path, mode, newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows([[line] for line in lines])

    def is_search_engine_url(self, url):
        # In WebCrawler/resources add more into ignoreUrls if needed
        search_engine_domains = self.ignore_list

        parsed_url = urlparse(url)
        netloc = parsed_url.netloc

        # Check if the netloc (domain) of the URL is in the list of search engine domains
        return any(search_engine_domain in netloc for search_engine_domain in search_engine_domains)

    @staticmethod
    def extract_search_engine_links(html_content):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Find the specific div element by its id ("search")
            search_div = soup.find('div', id='search')
            search_result_links = []

            if search_div:
                links = search_div.find_all('a', href=True)
                search_result_links = [link['href'] for link in links]
                return search_result_links
            return search_result_links
        except Exception as e:
            print(f"Error parsing HTML content: {e}")
            return ""

    def crawl_website_with_depth(self, csv_filename, depth_limit, start_url):
        self.link_queue.put((start_url, 0))
        self.save_content_to_csv('', csv_filename)
        separator = '||'
        while not self.link_queue.empty():
            current_url, current_depth = self.link_queue.get()

            # Check if the current URL is from a search engine and skip scraping if true
            print(current_url)
            if self.is_search_engine_url(current_url):
                #print(f"Skipping scraping for search engine URL: {current_url}")
                if current_depth == 0:
                    html_content = self.get_html_content(current_url)
                    valid_links = self.extract_search_engine_links(html_content)
                    time.sleep(2)
                    for link in valid_links[:5]:
                        self.link_queue.put((link, current_depth + 1))
            else:
                if current_depth > depth_limit or current_url in self.visited:
                    continue
                if self.is_valid_link(current_url):
                    self.visited.add(current_url)
                    html_content = self.get_html_content(current_url)
                    time.sleep(0.7)
                    if not html_content:
                        continue
                    # if self.has_product(html_content):
                    else:
                        scraped_url = self.driver.current_url
                        cleaned_content = self.clean_html_content(html_content)
                        cleaned_content = scraped_url + cleaned_content + '\n' + separator
                        self.save_content_to_csv(cleaned_content, csv_filename)
                else:
                    if self.is_pdf(current_url):
                        savetofile = current_url + separator
                        self.save_content_to_csv(savetofile, csv_filename)
                    else:
                        print("Weird")
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

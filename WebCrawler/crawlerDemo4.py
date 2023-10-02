import time
import os
import csv
import queue
from selenium import webdriver
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse


class WebCrawler:
    def __init__(self):
        self.driver = self.setup_headless_chrome()
        self.link_queue = queue.Queue()
        self.visited = set()

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
            return self.driver.page_source
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    @staticmethod
    def has_product(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return bool(soup.select('div[class*="product"]')) or bool(soup.select('div[id*="product"]'))

    def clean_html_content(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        # add class names you want to remove
        classes_to_remove = ['header', 'footer', 'nav', 'navbar']

        for class_name in classes_to_remove:
            elements_with_class = soup.find_all(class_=class_name)
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
        path = parsed_url.path
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
        # TODO: add standard filepath? ex. a results folder
        # Add folder for saved files
        folder_path = 'temp_files'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = f'temp_files/{csv_filename}'
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        mode = 'a' if os.path.exists(csv_filename) else 'w'
        with open(csv_filename, mode, newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows([[line] for line in lines])

    def crawl_website_with_depth(self, csv_filename, depth_limit, start_url):
        self.link_queue.put((start_url, 0))
        while not self.link_queue.empty():
            current_url, current_depth = self.link_queue.get()
            if current_depth > depth_limit or current_url in self.visited:
                continue
            self.visited.add(current_url)
            html_content = self.get_html_content(current_url)
            if not html_content:
                continue
            cleaned_content = self.clean_html_content(html_content)
            self.save_content_to_csv(cleaned_content, csv_filename)
            if current_depth < depth_limit:
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

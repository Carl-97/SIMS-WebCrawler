import time
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import csv
import queue

CONFIG = {
    'chrome_options': ['--headless', '--enable-javascript', '--disable-features=BlockThirdPartyCookies']
}


class WebCrawler:

    def __init__(self):
        self.driver = self.setup_headless_chrome()
        self.link_queue = queue.Queue()
        self.visited = set()

    def setup_headless_chrome(self):
        chrome_options = webdriver.ChromeOptions()
        for option in CONFIG['chrome_options']:
            chrome_options.add_argument(option)
        return webdriver.Chrome(options=chrome_options)

    def get_html_content(self, url):
        self.driver.get(url)
        return self.driver.page_source

    def has_product(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for selector in ['div[class*="product"]', 'div[id*="product"]']:
            if soup.select(selector):
                return True
        return False

    def extract_body_text(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag_name in ['header', 'footer', 'nav', 'navbar']:
            tag = soup.find(name=tag_name)
            if tag:
                tag.extract()
        return soup.body.get_text(strip=True) if soup.body else ""

    def find_links(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return [link['href'] for link in soup.find_all('a', href=True) if self.is_valid_link(link['href'])]

    def is_valid_link(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and not url.lower().endswith('.pdf')

    def save_to_csv(self, lines, csv_filename):
        write_mode = 'a' if os.path.exists(csv_filename) else 'w'
        with open(csv_filename, write_mode, newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for line in lines:
                csv_writer.writerow([line.strip()])

    def crawl_website_with_depth(self, start_url, csv_filename, depth_limit=1):
        self.link_queue.put((start_url, 0))

        while not self.link_queue.empty():
            current_url, current_depth = self.link_queue.get()

            if current_url in self.visited or current_depth > depth_limit:
                continue

            print("Currently on:", current_url)
            self.visited.add(current_url)
            html_content = self.get_html_content(current_url)

            for link in self.find_links(html_content):
                self.link_queue.put((link, current_depth + 1))

            text_content = f"This URL: {current_url}\n"
            text_content += self.extract_body_text(html_content)
            self.save_to_csv([current_url], 'resources/visited.csv')
            self.save_to_csv(text_content.split('\n'), csv_filename)

    def close_browser(self):
        self.driver.quit()


# Testing the class
if __name__ == '__main__':
    with WebCrawler() as wc:
        test_file = 'test_method.csv'
        test_url = 'https://www.e-nummersok.se/...'
        wc.crawl_website_with_depth(test_url, test_file)

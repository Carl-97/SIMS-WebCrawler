from selenium import webdriver
from bs4 import BeautifulSoup
import os
import csv
import requests


class WebCrawler:
    E_NUMMER_URL = 'https://www.e-nummersok.se/sok?Query='
    RSK_URL = 'https://www.rskdatabasen.se/sok?Query='

    def __init__(self):
        # Initialize a headless Chrome WebDriver
        self.driver = self.setup_headless_chrome()
        # Use a set to store visited URLs for faster duplicate checking
        self.visited = set()

    def setup_headless_chrome(self):
        # Configure and return a headless Chrome WebDriver instance
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--enable-javascript')
        chrome_options.add_argument('--disable-features=BlockThirdPartyCookies')
        return webdriver.Chrome(options=chrome_options)

    def get_html_content(self, url):
        # Use the requests library to fetch the HTML content of a URL
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def has_product(self, html_content):
        # Check if the HTML content contains product-related elements
        soup = BeautifulSoup(html_content, 'html.parser')
        selectors = ['div[class*="product"]', 'div[id*="product"]']
        for selector in selectors:
            if soup.select(selector):
                return True
        return False

    def is_pdf(self, url):
        # checks if its end with .pdf
        return url.lower().endswith('.pdf')

    def extract_text_content(self, html_content):
        # Extract text content from HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        body_content = soup.body
        if body_content:
            return body_content.get_text()
        return soup

    def save_to_csv(self, text_content, csv_filename):
        # Save text content to a CSV file
        lines = [line.strip() for line in text_content.strip().split('\n') if line.strip()]
        mode = 'w' if not os.path.exists(csv_filename) else 'a'
        with open(csv_filename, mode, newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for line in lines:
                csv_writer.writerow([line])

    def process_page(self, url, csv_filename):
        # Process a webpage: download, check for products, and save
        if url in self.visited:
            print("Already visited:", url)
            return
        print("Currently on:", url)
        self.visited.add(url)
        html_content = self.get_html_content(url)
        self.save_to_csv(url, 'resources/visited.csv')
        text_content = "this url:" + url
        if self.has_product(html_content):
            text_content += self.extract_text_content(html_content)
        self.save_to_csv(text_content, csv_filename)

    def scrape_databank(self, filename, id_nr, brand=None):
        # Scrape e-nummersok and rskdatabasen for a given ID number
        e_nummer_url = WebCrawler.E_NUMMER_URL + str(id_nr)
        rsk_url = WebCrawler.RSK_URL + str(id_nr)
        self.process_page(e_nummer_url, filename)
        self.process_page(rsk_url, filename)

    def crawl_website_with_depth(self, csv_filename, depth_limit, start_url):
        # Crawl a website up to a specified depth
        self.process_page(start_url, csv_filename)
        current_depth = 0

        while current_depth < depth_limit:
            new_links = set()

            for url in self.visited:
                html_content = self.get_html_content(url)
                links = self.find_links(html_content)
                new_links.update(links)

            for link in new_links:
                self.process_page(link, csv_filename)

            current_depth += 1

    def find_links(self, html_content):
        # Find valid website links in HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a', href=True)
        valid_links = []
        for link in links:
            href = link.get('href')
            if self.valid_website_link(href) and not self.is_pdf(href):
                valid_links.append(href)
        return valid_links

    def valid_website_link(self, url):
        # Check if a URL is a valid website link
        return url.startswith(('http://', 'https://'))


if __name__ == '__main__':
    test_file = 'test_method.csv'
    depth = 1
    url = 'https://www.e-nummersok.se/lista/plintsystem-plint-och-kabelmarkning-apparats/plintsystem-for-skenmontage/weidmuller/plint-sakr-pa-m-2920154-14020'

    wc = WebCrawler()
    wc.crawl_website_with_depth(test_file, depth, url)
    wc.close_browser()

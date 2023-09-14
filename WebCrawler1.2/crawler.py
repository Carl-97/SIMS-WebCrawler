from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import csv
import queue


class WebCrawler:
    def __init__(self):
        self.driver = self.setup_headless_chrome()
        self.link_queue = queue.Queue()

    def setup_headless_chrome(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--enable-javascript')
        chrome_options.add_argument('--disable-features=BlockThirdPartyCookies')
        return webdriver.Chrome(options=chrome_options)

    def get_html_content(self, url):
        self.driver.get(url)
        return self.driver.page_source

    # Find valid links only, ex: links that starts with 'www'
    def find_links(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a')

        valid_links = []
        for link in links:
            href = link.get('href')
            if href:
                parsed_url = urlparse(href)
                if parsed_url.scheme and parsed_url.netloc:
                    valid_links.append(href)

        return valid_links

    def extract_text_content(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    def save_to_csv(self, text_content, csv_filename):
        # TODO: add a standard filepath
        file_path = ''
        # Split the text content by newline characters and remove empty lines
        lines = [line.strip() for line in text_content.strip().split('\n') if line.strip()]

        if not os.path.exists(csv_filename):
            # Save the text content to a CSV file with 'utf-8' encoding
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                for line in lines:
                    # Write each line as a separate row in the CSV file
                    csv_writer.writerow([line])
        else:
            # Append text to existing file
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                for line in lines:
                    # Write each line as a separate row in the CSV file
                    csv_writer.writerow([line])

    def crawl_website_with_depth(self, start_url, csv_filename, depth_limit):
        self.link_queue.put(start_url)
        current_depth = 0

        while not self.link_queue.empty() and current_depth < depth_limit:
            # TODO: add a check if links is valid and if not concat to former link? If wanting to concat the link,
            #  change the method find_links to find all
            current_url = self.link_queue.get()
            html_content = self.get_html_content(current_url)
            print(html_content)
            links = self.find_links(html_content)

            print(f"Found Links at depth {current_depth}:")
            for link in links:
                print(link)
                self.link_queue.put(link)

            text_content = self.extract_text_content(html_content)
            self.save_to_csv(text_content, csv_filename)

            current_depth += 1

    def close_browser(self):
        self.driver.quit()


if __name__ == "__main__":
    url = ('https://www.bossard.com/eshop/se-sv/products/fastening-technology/standard-fastening-elements/nuts'
           '/square-nuts/square-nuts/p/147')
    filename = 'web_data.csv'
    depth = 2
    crawler = WebCrawler()
    crawler.crawl_website_with_depth(url, filename, depth)
    crawler.close_browser()

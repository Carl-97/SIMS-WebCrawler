import time

from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os
import csv
import queue
import requests


class WebCrawler:
    def __init__(self):
        # self.url = ''
        # driver is source?
        self.driver = self.setup_headless_chrome()
        self.link_queue = queue.Queue()
        self.visited = ['']

    def get_visited(self):
        return self.visited

    '''def set_url(self, url):
        self.url = url'''

    def setup_headless_chrome(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--enable-javascript')
        chrome_options.add_argument('--disable-features=BlockThirdPartyCookies')
        return webdriver.Chrome(options=chrome_options)

    def get_html_content(self, url):
        self.driver.get(url)
        return self.driver.page_source

    def has_product(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        # product = soup.find('product')
        selector = 'div[class*="product"]'
        matching_div = soup.select(selector)
        if matching_div:
            #print("Finns")
            return True
        selector2 = 'div[id*="product"]'
        matching_div = soup.select(selector2)
        if matching_div:
            #print("Finns")
            return True
        return False

    def get_html_body(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        # gets all 'a' elements that have a href atribute

        header = soup.find('header')
        if header:
            header.extract()
        footer = soup.find('footer')
        if footer:
            footer.extract()
        # nav = soup.find('nav')
        # if nav:
        # nav.extract()

        navbar = soup.find(class_='navbar')
        if navbar:
            navbar.extract()

        body = soup.find('body').get_text()
        return body

    # Find valid links only, ex: links that starts with 'www'
    def find_links(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        # gets all 'a' elements that have a href attribute
        links = soup.find_all('a', href = True)
        # filter out non website links
        # url = [link for link in links if self.valid_website_link(link)]

        valid_links = []
        for link in links:
            href = link.get('href')
            parsed_url = urlparse(href)

            if parsed_url.scheme and parsed_url.netloc:
                # unsure if validate does anything
                if self.valid_website_link(href):
                    if not self.is_pdf(href):  # still can download documents
                        valid_links.append(href)
        return valid_links

    def is_pdf(self, url):
        # checks if its end with .pdf
        return url.lower().endswith('.pdf')

    def valid_website_link(self, url):
        x = url.startswith(('http://', 'https://'))
        #print("valid" , x)
        return x

    def extract_text_content(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        # Extract content only from the <body> tag
        body_content = soup.body
        if body_content:
            return body_content.get_text()
        return soup

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

    def crawl_website_with_depth(self, csv_filename, depth_limit, url):
        self.link_queue.put(url)
        current_depth = 0

        while not self.link_queue.empty() and current_depth <= depth_limit:

            # TODO: add a check if links is valid and if not concat to former link? If wanting to concat the link,
            #  change the method find_links to find all
            current_url = self.link_queue.get()

            alreadVisited = False
            for visitedurl in self.visited:
                if visitedurl == current_url:
                    alreadVisited = True
                    print("already visited")
            if not alreadVisited:
                print("curently on: ", current_url)
                self.visited.append(current_url)
                html_content = self.get_html_content(current_url)
                # TODO: optimize extraction, get_html_body and extract_text_content
                self.add_links(html_content, current_depth)
                self.save_to_csv(current_url, 'resources/visited.csv')
                text_content = "this url:" + url
                text_content += self.get_html_body(html_content)
                #text_content = "this url:" + self.url
                #text_content += self.extract_text_content(body)
                self.save_to_csv(text_content, csv_filename)
                # saves it to the visited csv file
                current_depth += 1

    # TODO: fix so that it looks on both e-nr and rsk and try to check if data exists and if not send back boolean false?
    def scrape_data(self, filename, id_nr, extra=None):
        e_nr_url = 'https://www.e-nummersok.se/sok?Query=' + str(id_nr)
        rsk_nr_url = 'https://www.rskdatabasen.se/sok?Query=' + str(id_nr)

        e_nr_url = self.check_url(e_nr_url, 'E-nr')
        rsk_nr_url = self.check_url(rsk_nr_url, 'RSK')

        if e_nr_url or rsk_nr_url:
            if e_nr_url and rsk_nr_url:
                print('Match on both, better compare extraInfo')
                # TODO: Compare data on the webpages if one of them is more likely to be correct
                html_content = self.get_html_content(e_nr_url)
                text_content = self.extract_text_content(html_content)
                if extra in text_content:
                    print(e_nr_url)
                    self.save_to_csv(text_content, 'e_nr_content.csv')

                html_content = self.get_html_content(rsk_nr_url)
                text_content = self.extract_text_content(html_content)
                if extra in text_content:
                    print(rsk_nr_url)
                    self.save_to_csv(text_content, 'rsk_nr_content.csv')
                return
            elif e_nr_url:
                #self.set_url(e_nr_url)
                self.driver.refresh()
                self.crawl_website_with_depth(filename, 0, e_nr_url)
            else:
                #self.set_url(rsk_nr_url)
                self.driver.refresh()
                self.crawl_website_with_depth(filename, 0, e_nr_url)
        else:
            print('Found no matches')

    def check_url(self, url, identifier):
        #self.set_url(url)
        self.driver.get(url)
        current_url = self.get_current_url()

        if url == current_url:
            print(f'No hit on {identifier}')
            return ''
        else:
            print(f'Found something at {identifier}')
            return current_url

    # Some URLs don't get updated immediately, so this method waits for it to update and sends back the new URL
    def get_current_url(self):
        initial_url = self.driver.current_url
        current_url = initial_url
        i = 0
        while i < 3:
            current_url = self.driver.current_url
            if current_url != initial_url:
                break
            time.sleep(1)
            i += 1
        print(f'Initial URL: {initial_url}')
        print(f'Current URL: {current_url}')
        return current_url

    def add_links(self, html_content, current_depth):
        links = self.find_links(html_content)
        for link in links:
            self.link_queue.put(link)

    def close_browser(self):
        self.driver.quit()


# Testing for some methods
if __name__ == '__main__':
    test_file = 'test_method.csv'
    depth = 1
    url = 'https://www.e-nummersok.se/lista/plintsystem-plint-och-kabelmarkning-apparats/plintsystem-for-skenmontage/weidmuller/plint-sakr-pa-m-2920154-14020'

    wc = WebCrawler()
    '''wc.set_url(url)
    wc.crawl_website_with_depth(test_file, depth)
    wc.close_browser()'''

    file = 'test.csv'
    brand = 'Weidmüller'
    wc.scrape_data(file, 2920154, brand)
    wc.close_browser()

import time
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os
import csv
import queue


class WebCrawler:
    def __init__(self):
        # self.url = ''
        # driver is source?
        self.driver = self.setup_headless_chrome()
        self.link_queue = queue.Queue()
        self.visited = set()

    def get_visited(self):
        return self.visited

    '''def set_url(self, url):
        self.url = url'''

    @staticmethod
    def setup_headless_chrome():
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

    @staticmethod
    def get_html_body(html_content):
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

    @staticmethod
    def clean_html_content(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag_name in ['header', 'footer', 'nav', 'navbar']:
            tag = soup.find(tag_name)
            if tag:
                tag.extract()
        return soup.body.get_text()

    def save_to_csv(self, text_content, csv_filename):
        # TODO: add a standard filepath
        file_path = ''
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
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
            self.save_to_csv(cleaned_content, csv_filename)
            if current_depth < depth_limit:
                for link in self.find_links(html_content):
                    self.link_queue.put((link, current_depth + 1))

    @staticmethod
    def extract_text_content(html_content):
        # Extract text content from HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        body_content = soup.body
        if body_content:
            return body_content.get_text()
        return soup.body.get_text()

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
                    print(f'Match {extra}, seems to be found on: {e_nr_url}')
                    self.save_to_csv(text_content, 'e_nr_content.csv')

                html_content = self.get_html_content(rsk_nr_url)
                text_content = self.extract_text_content(html_content)
                if extra in text_content:
                    print(f'Match {extra}, seems to be found on: {rsk_nr_url}')
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
        while i < 5:
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
    depth = 0
    url = 'https://www.e-nummersok.se/lista/plintsystem-plint-och-kabelmarkning-apparats/plintsystem-for-skenmontage/weidmuller/plint-sakr-pa-m-2920154-14020'

    # Test crawl depth, be careful with this
    wc = WebCrawler()
    wc.crawl_website_with_depth(test_file, depth, 'https://www.e-nummersok.se/lista/kontaktorer-startapparater-kontaktormanovrera/kontaktorer-kontaktorkombinationer-med-tillbe/siemens/varistor-127-240vac150-250vdc-3266972-27334')

    # Crawl specific urls based on id and if it can find the right one
    file = 'test.csv'
    brand = 'Weidmüller'
    wc.scrape_data(file, 2920154, brand)
    wc.close_browser()

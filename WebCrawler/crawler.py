from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os
import csv
import queue
import requests
    
class WebCrawler:
    def __init__(self):
        self.url =''
    	#driver is source?
        self.driver = self.setup_headless_chrome()
        self.link_queue = queue.Queue()
        self.visited = ['https://www.bossard.com/eshop/se-sv/products/fastening-technology/standard-fastening-elements/nuts/square-nuts/square-nuts/p/147']
        self.ignorelist = []        
    def get_visited(self):
        return self.visited
    def setUrl(self, url):
        self.url = url
    # TODO: add a function that reads an excel file and checks attributes that might be usable in crawl, ex: E-nr
    def setup_headless_chrome(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--enable-javascript')
        chrome_options.add_argument('--disable-features=BlockThirdPartyCookies')
        return webdriver.Chrome(options=chrome_options)

    def get_html_content(self, url):
        self.driver.get(url)
        return self.driver.page_source
    
    #tar bort delar av hemsidan
    def has_product(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        #product = soup.find('product')
        selector = 'div[class*="product"]'
        matching_div = soup.select(selector)
        if matching_div: 
            print("Finns")
            return True
        selector2 = 'div[id*="product"]'
        matching_div = soup.select(selector2)
        if matching_div: 
            print("Finns")
            return True
        return False
    def get_html_body(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        #gets all 'a' elements that have a href atribute
        header = soup.find('header')
        if header: 
            header.extract()
        footer = soup.find('footer')
        if footer:
            footer.extract()
        nav = soup.find('nav')
        if nav:
            nav.extract()
        
        navbar = soup.find(class_='navbar')
        if navbar:
            navbar.extract()
         
        body= soup.find('body').get_text()
        return body
        
    # Find valid links only, ex: links that starts with 'www'
    def find_links(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        #gets all 'a' elements that have a href atribute
        links = soup.find_all('a', href = True)
        #filter out non website links
       # websitelinks = [link for link in links if self.valid_website_link(link)]
        valid_links = []
        for link in links:
            href = link.get('href')
            parsed_url = urlparse(href)
            
            if parsed_url.scheme and parsed_url.netloc:
               #unsure if validate does anything
                if self.valid_website_link(href):
                    if not self.is_pdf(href): #still can download docements
                        valid_links.append(href)
        return valid_links
    
    def is_pdf(self, url):
        #checks if its end with .pdf
        return url.lower().endswith('.pdf')

    def valid_website_link(self, url): 
        x = url.startswith(('http://', 'https://'))
        #print("valid" , x)
        return x
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

    def crawl_website_with_depth(self, csv_filename, depth_limit):
        self.link_queue.put(self.url)
        current_depth = 0

        while not self.link_queue.empty() and current_depth < depth_limit:
            
            # TODO: add a check if links is valid and if not concat to former link? If wanting to concat the link,
            #  change the method find_links to find all
            current_url = self.link_queue.get()
            ignore = False
            for ignorelist in self.ignorelist:
                if ignorelist == current_url:
                    ignore= True
                    print("in the ignor list")
            if ignore == False:
                alreadVisited = False
                for visitedurl in self.visited:
                    if visitedurl == current_url:
                        alreadVisited = True
                        print("already visited")
                if alreadVisited == False or current_depth == 0:      
                    if alreadVisited == False:
                        self.visited.append(current_url)
                        print("curently on: " , current_url)
                    self.visited.append(current_url)
                    html_content = self.get_html_content(current_url)
                    self.add_Links(html_content, current_depth)
                    self.save_to_csv(current_url,'visited.csv')
                    #print(html_content)
                    if self.has_product(html_content):
                        body = self.get_html_body(html_content);
                        #text_content = "this url:" + self.url
                        body += "this url: " + self.url
                        self.save_to_csv(body, csv_filename)
                #saves it to the visited csv file
                current_depth += 1
    
    def add_Links(self, html_content, current_depth):
        # TODO: prints the links found on the page
        links = self.find_links(html_content)
            
        print(f"Found Links at depth {current_depth}:")
        for link in links:
         #   print(link)
            self.link_queue.put(link)

    def close_browser(self):
        self.driver.quit()
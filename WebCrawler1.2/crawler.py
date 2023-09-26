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
        self.visited = ['https://www.bossard.com/eshop/za-en']
    
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
    def get_html_body(self, url):
        #finds and remove header and 
        header_content = self.driver.find_element_by_tag_name("header").txt
        footer_content = self.driver.find_element_by_tag_name("footer").txt
        navbar_content = self.driver.find_element_by_tag_name("header").txt
        self.driver.execute_script("arguments[0].parentNode.removeChild(arguments[0])", header_content)
        self.driver.execute_script("arguments[0].parentNode.removeChild(arguments[0])", footer_content)
        self.driver.execute_script("arguments[0].parentNode.removeChild(arguments[0])", navbar_content)
        
        #get body content
        body_content = self.driver.find_element_by_tag_name("body").txt
        return body_content
    
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
            
            alreadVisited = False
            for visitedurl in self.visited:
                if visitedurl == current_url:
                    alreadVisited = True
                    print("already visited")
            if alreadVisited == False:
                print("curently on: " , current_url)
                self.visited.append(current_url)
                html_content = self.get_html_content(current_url)
                body = self.get_html_content(current_url);
                self.add_Links(html_content, current_depth)
                
               
                self.save_to_csv(current_url,'visited.csv')
                #print(html_content)
            
                text_content = "this url:" + self.url
                
                #text_content += self.extract_text_content(html_content)
                #text_content
                #self.save_to_csv(text_content, csv_filename)
                
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



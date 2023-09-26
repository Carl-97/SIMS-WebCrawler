import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from crawler import WebCrawler


startUrl = "https://www.bossard.com/eshop/se-sv/products/fastening-technology/standard-fastening-elements/nuts/square-nuts/square-nuts/p/147"
filename = 'web_data.csv'
    #deep is amount of websites url we searched from 
depth = 10
crawlertest = WebCrawler()
crawlertest.setUrl(startUrl)
crawlertest.crawl_website_with_depth(filename, depth)
array = crawlertest.get_visited()
for x in array:
    print(x)
 

import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from crawler import WebCrawler

excel_file = 'e-nummer.xlsx'

df = pd.read_excel(excel_file)
crawlerSize= 0; #knowing a  mount of items can be useful #21217
i = 0 
crawlertest = []
for index, row in df.iterrows():
    
    #asuming we have thise rows in the excel file
    #startAritikel = row['Artikelnummer']
    #startArtikelbeskrivning = row['Artikelbeskrivning']
    #startTypbeteckning = row['Typbeteckning']
    #startKompletterandeInfo = row['Kompletterande info']
    #startVarumärke= row['Varumärke']
    Size = len(crawlertest) 
    starEnumer = row['E-nummer']
    crawlertest.append( WebCrawler()) 
    startUrl = ('https://www.e-nummersok.se/sok?Query='+ str(starEnumer))
    #https://www.e-nummersok.se/sok?Query=2920154
    filename = 'web_data.csv'
    #deep is amount of websites url we searched from 
    depth = 10
    crawlertest[i].set_url(startUrl)
    crawlertest[i].crawl_website_with_depth(filename, depth)
    array = crawlertest[i].get_visited()
    for x in array:
        print(x)
    i = i + 1

i=0
for crawler in crawlertest[i]:
    crawler[i].close_browser()

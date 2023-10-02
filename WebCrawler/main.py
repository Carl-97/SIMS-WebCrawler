from crawler import WebCrawler
import pandas as pd
inputfile = './resources/apendo.xlsx'
outputfile = 'web_data.csv'
rskoutputfile = 'rks.csv'
enumoutputfile = 'enum.csv'
    #url = 'https://www.e-nummersok.se/lista/plintsystem-plint-och-kabelmarkning-apparats/plintsystem-for-skenmontage/weidmuller/plint-sakr-pa-m-2920154-14020'

    #excel_file = '/resources/e-nummer_20230915.xlsx'

df = pd.read_excel(inputfile)
crawlerSize= 0; #knowing a  mount of items can be useful #21217
i = 0 
crawlertest = []
for index, row in df.iterrows():
    wc = WebCrawler()
  
    
 
    Size = len(crawlertest) 
    starEnumer = row['Artikelnummer']
    
    crawler = WebCrawler()
    
    #crawlertest.append( WebCrawler()) 
    
    startUrl = ('https://www.e-nummersok.se/sok?Query='+ str(starEnumer))
    
    #
    # deep is amount of websites url we searched from 
    
    depth = 0
    crawlertest.append(crawler)
    #check if its enum or rsk
    #its not
    #sök artikel + brand
    crawlertest[i].set_url(startUrl)
    crawlertest[i].crawl_website_with_depth(outputfile, depth, startUrl)
    
    array = crawlertest[i].get_visited()
    for x in array:
        print(x)
    i = i + 1

y=0
for crawler in crawlertest[y]:
    crawler[y].close_browser()
from ExcelManip import excelmanip as em
from WebCrawler.crawler import WebCrawler

if __name__ == '__main__':
    manipulator = em.ExcelManip('resources/sample.xlsx')
    data = manipulator.pre_process()
    wc = WebCrawler()
    filename = 'data.csv'

    for dictionary in data:
        if 'rsk' in dictionary:
            if 'brand' in dictionary:
                rsk_val = dictionary['rsk']
                print(rsk_val)
                brand_value = dictionary['brand']
                wc.scrape_databank(filename, rsk_val, brand_value)
            else:
                print("This row has RSK only.")
                rsk_val = dictionary['rsk']
                wc.scrape_databank(filename, rsk_val, None)
        else:
            print('Better use a search engine...')
    print("------")


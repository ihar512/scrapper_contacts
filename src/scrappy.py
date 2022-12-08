import logging
import os
import pandas as pd
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
logging.getLogger('scrapy').propagate = False


class MailSpider(scrapy.Spider):
    name = 'email'
    def parse(self, response):
        links = LxmlLinkExtractor(allow=()).extract_links(response)
        links = [str(link.url) for link in links]
        links.append(str(response.url))
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_link) 
            
    def parse_link(self, response):
        for word in self.reject:
            if word in str(response.url):
                return
        html_text = str(response.text)
        mail_list = re.findall('\w+@\w+\.{1}\w+', html_text)
        dic = {'email': mail_list, 'link': str(response.url)}
        df = pd.DataFrame(dic)
        df.to_csv(self.path, mode='a', header=False)
        df.to_csv(self.path, mode='a', header=False)


def get_info(path, reject=[]):
    
    create_file(path)
    df = pd.DataFrame(columns=['email', 'link'], index=[0])
    df.to_csv(path, mode='w', header=True)
    
    # print('Collecting Google urls...')
    # google_urls = get_urls(tag, n, language)

    # read company urls
    # replace google_urls list with list of company urls
    company_urls = ['www.nerdyboyproductions.com','www.DesignProductionsLLC.com','www.laserandlighting.com']
    
    print('Searching for emails...')
    process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0'})
    process.crawl(MailSpider, start_urls=company_urls, path=path, reject=reject)
    process.start()
    
    print('Cleaning emails...')
    df = pd.read_csv(path, index_col=0)
    df.columns = ['email', 'link']
    df = df.drop_duplicates(subset='email')
    df = df.reset_index(drop=True)
    df.to_csv(path, mode='w', header=True)
    return df


def ask_user(question):
    response = input(question + ' y/n' + '\n')
    if response == 'y':
        return True
    else:
        return False


def create_file(path):
    response = False
    if os.path.exists(path):
        response = ask_user('File already exists, replace?')
        if response == False: return 
    with open(path, 'wb') as file: 
        file.close()


if __name__ == "__main__":
    path = os.getcwd() + '\scrappy.csv'
    bad_words = ['facebook', 'instagram', 'youtube', 'twitter', 'wiki']
    output = get_info(path, bad_words)
    print(output)
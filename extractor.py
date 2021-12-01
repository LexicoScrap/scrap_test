from requests import get
from scrapy import Selector

from articles_data import Articles, Article

CNEWS_PATH = "https://www.cnews.fr"
HEADERS = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

class Extractor(Articles, Article):

    def __init__(self, media):
        self.media = media

class CNewsExctraction(Extractor):

    def __init__(self, corpus_data):
        super().__init__("CNews")
        self.corpus_data = corpus_data

    def extract_urls(self):
        i = 0
        while (True):
            print('page '+str(i))
            if i == 0:
                url_end = self.corpus_data.searched_word
            else:
                url_end = self.corpus_data.searched_word + "?page=" +str(i)
            response = get(CNEWS_PATH + "/rechercher/"+url_end, headers=HEADERS, allow_redirects= False)
            source = None
            status = response.status_code 
            if status == 200 :
                source = response.text
            if source:
                selector = Selector(text=source)
                # print(selector.xpath("//div[@class='search-results article-suggests']/a/@href").get())
                if selector.xpath("//div[@class='search-results article-suggests']/a/@href").get() is not None:
                    for href in selector.xpath("//div[@class='search-results article-suggests']/a/@href").extract():
                        article = Article()
                        article.url = href
                        print(article.url)
                        self.corpus_data.results.append(article)      
                else:
                    break
            i = i+1
        

    def extract_articles_data(self):
        index = 1
        for article in self.corpus_data.results:
            print(f'{index} {len(self.corpus_data.results)}')
            if len(self.corpus_data.results) >= index:
                article.id = str(index)
                self.extract_cnews_data(article)
                if article.content == 'no_access' or self.corpus_data.searched_word not in article.content:
                    continue
                self.corpus_data.articles.append(article)
                if self.corpus_data.max_size_result == index:
                    break
            index = index+1

    def extract_cnews_data(self, article):
        response = get(CNEWS_PATH + article.url, headers=HEADERS, allow_redirects=False)
        source = None
        status = response.status_code
        print(status) 
        if status == 200 :
            print('status ok')
            source = response.text
        else:
            print('status_ko')
            article.title = 'no access'
            article.author = 'no access'
            article.date = 'no date'
            article.content = 'no access'
            article.tag = 'no tag'
            return 
        if source:
            selector = Selector(text=source)
            sel_title = selector.xpath("//h1/text()").extract()
            sel_author = selector.xpath("//span[@class='video-auteur']/span/text()").extract()
            sel_date = selector.xpath('//time[@datetime]/text()').extract()
            sel_content = selector.xpath(".//p/text()").extract()
            sel_tag = self.find_tag(selector)
            article.title = self.clean_title(sel_title)
            article.author = self.clean_author(sel_author)
            article.date = self.clean_date(sel_date)
            article.content = self.clean_content(sel_content)
            article.tag= sel_tag[0]
        article.print_article()

    def find_tag(self, selector):
        sel_tag = selector.xpath("//div[@class='article-tag']/a/text()").extract() 
        if sel_tag != []:
            return sel_tag
        else:
            sel_tag = selector.xpath("//div[@class='video-tag']/a/text()").extract()
        if sel_tag != []:
            return sel_tag
        else:
            return "notag"  

    def clean_title(self, sel_title):
        if not sel_title:
            return 'no title'
        string_title = sel_title[0]
        string_title = string_title.replace('\xa0', ' ')
        return string_title

    def clean_author(self, sel_author):
        if not sel_author:
            return "no author"
        string_author = sel_author[0]
        string_author = string_author.replace('\n','')
        string_author = string_author[:-2]
        return string_author

    def clean_date(self, sel_date):
        if not sel_date:
            return 'no date'
        string_date = sel_date[0][:-8]
        return string_date
        
    def clean_content(self, sel_content):
        content = ""
        for paragraph in sel_content:
            content += paragraph
        content = content.replace('\xa0', '')
        content = content.replace('\n', '')
        content = content.replace('@', '')
        content = content.replace('À voir aussi', '')
        content = content.replace('Thèmes associés', '')
        content = content.replace('À suivre aussi', '')
        content = content.replace('Ailleurs sur le web', '')
        content = content.replace('Dernières actualités', '')
        return content


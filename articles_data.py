from datetime import datetime
from requests import get
from scrapy import Selector
import os.path
import json

IRAMUTEQ_SAVE_PATH = '/media/dleroux/DATA/corpus_iramuteq'
JSON_SAVE_PATH = '/media/dleroux/DATA/json_extraction'
CNEWS_PATH = "https://www.cnews.fr"
HEADERS = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

class Articles:

    def __init__(self, searched_word, maximum_size_res):
        self._searched_word = searched_word
        self._results = []
        self.articles = []
        self.maximum_size_res = maximum_size_res

    @property
    def searched_word(self):
        return self._searched_word

    @searched_word.setter
    def searched_word(self, value):
        self._searched_word = value

    @property
    def results(self):
        return self._results

    @results.setter
    def results(self, value):
        self._results = value

    def extract_url(self):
        i = 0
        while (True):
            print('page '+str(i))
            if i == 0:
                url_end = self.searched_word
            else:
                url_end = self.searched_word + "?page=" +str(i)
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
                        self.results.append(article)
                    
                else:
                    break
            i = i+1
        

    def extract_articles_data(self, max_size_result):
        index = 1
        for article in self.results:
            print(f'{index} {len(self.results)}')
            if len(self.results) >= index:
                article.id = str(index)
                article.extract_cnews_data()
                if article.content == 'no_access':
                    continue
                self.articles.append(article)
                if max_size_result == index:
                    break
            index = index+1


    def save_to_iramuteq_txt_files(self):
        print('save to Iramuteq"')
        complete_name = os.path.join(IRAMUTEQ_SAVE_PATH, self.searched_word+".txt")
        corpus = ''
        for article in self.articles:
            if article is not None and article.id is not None:
                corpus = corpus + article.to_iramuteq_txt()
        with open(complete_name,"w+") as txt_file:
            txt_file.write(corpus)
        

    def to_dict(self):
        return {self.searched_word : {article.id : article.to_dict() for article in self.articles}}

    def save_to_json(self):
        dump = dump_dict_to_json(self.to_dict())
        save_as_json_file(dump, self.searched_word)


class Article:

    def __init__(self):
        self._id = None
        self._title = None
        self._date = None
        self._author = None
        self._url = None
        self._content = None
        self._thema = None
        self._tag = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def thema(self):
        return self._thema

    @thema.setter
    def thema(self, value):
        self._thema = value

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    def extract_cnews_data(self):
        response = get(CNEWS_PATH + self.url, headers=HEADERS, allow_redirects=False)
        source = None
        status = response.status_code
        print(status) 
        if status == 200 :
            print('status ok')
            source = response.text
        else:
            print('status_ko')
            self.title = 'no access'
            self.author = 'no access'
            self.date = 'no date'
            self.content = 'no access'
            self.tag = 'no tag'
            return 
        if source:
            selector = Selector(text=source)
            sel_title = selector.xpath("//h1/text()").extract()
            sel_author = selector.xpath("//span[@class='video-auteur']/span/text()").extract()
            sel_date = selector.xpath('//time[@datetime]/text()').extract()
            sel_content = selector.xpath(".//p/text()").extract()
            sel_tag = find_tag(selector)
            self.title = clean_title(sel_title)
            self.author = clean_author(sel_author)
            self.date = clean_date(sel_date)
            self.content = clean_content(sel_content)
            self.tag= sel_tag[0]
        self.print_article()


    def to_iramuteq_txt(self):
        balises = self.create_iramuteq_balises()
        content = str(self.title) + '. ' + str(self.content)
        content = content.replace('*',' ')
        text = balises + '\n' + content + '\n' 
        text = text.encode('cp1253','strict')
        return text

    def create_iramuteq_balises(self):
        text_balise = '****'
        author_balise = self.iramuteq_author_balise()
        date_balise = self.iramuteq_date_balise()
        id_balise = self.iramuteq_id_balise()
        thema_balise = self.iramuteq_thema_balise()
        tag_balise = self.iramuteq_tag_balise()
        return text_balise + ' ' + id_balise + ' ' + author_balise + ' ' + date_balise + ' ' + thema_balise + ' ' + tag_balise

    def iramuteq_author_balise(self):
        print(f'{self.id} {self._author} {self.title}')
        return '*author_'+ clean_balise_string(self.author)

    def iramuteq_date_balise(self):
        if self.date == 'no date':
            return '*date_nodate'
        date = datetime.strptime(self.date, '%d/%m/%Y')
        reverse_date = date.strftime('%Y%m')
        return '*date_' + reverse_date

    def iramuteq_id_balise(self):
        return '*id_'+ self.id

    def iramuteq_thema_balise(self):
        return '*thema_' + clean_balise_string(self.url.split('/')[1])

    def iramuteq_tag_balise(self):
        return '*tag_' + clean_balise_string(self.tag)

    def to_dict(self):
        return {"title" : self.title, "url": self.url, "author": self.author, "date": self.date, "content": self.content}


    def print_article(self):
            print('-------------------------------------------------')
            print("article n°"+self.id)
            print("url: " + self.url)
            print("title: " + self.title)
            print("author: " + self.author)
            print("date: " + self.date)
            print("tag: " + self.tag)
            print("content: " + self.content)

"""UTILITIES"""

def find_tag(selector):
    sel_tag = selector.xpath("//div[@class='article-tag']/a/text()").extract() 
    if sel_tag != []:
        return sel_tag
    else:
        sel_tag = selector.xpath("//div[@class='video-tag']/a/text()").extract()
    if sel_tag != []:
        return sel_tag
    else:
        return "notag"  
        


def clean_title(sel_title):
    if not sel_title:
        return 'no title'
    string_title = sel_title[0]
    string_title.replace('\xa0', ' ')
    return string_title

def clean_author(sel_author):
    if not sel_author:
        return "no author"
    string_author = sel_author[0]
    string_author = string_author.replace('\n','')
    string_author = string_author[:-2]
    return string_author

def clean_date(sel_date):
    if not sel_date:
        return 'no date'
    string_date = sel_date[0][:-8]
    return string_date
    
def clean_content(sel_content):
    content = ""
    for paragraph in sel_content:
        content += paragraph
    content = content.replace('\xa0', '')
    content = content.replace('\n', '')
    content = content.replace('À voir aussi', '')
    content = content.replace('Thèmes associés', '')
    content = content.replace('À suivre aussi', '')
    content = content.replace('Ailleurs sur le web', '')
    content = content.replace('Dernières actualités', '')
    return content


def dump_dict_to_json(json_dict):
    return json.dumps(json_dict, ensure_ascii= False, indent = 4)

def save_as_json_file(json_res, searched_word):    
    complete_name = os.path.join(JSON_SAVE_PATH, searched_word +".json")
    with open(complete_name, "w+") as json_file:
        json_file.write(json_res)
    
def clean_balise_string(string_to_clean):
    string_to_clean = string_to_clean.lower()
    string_to_clean = string_to_clean.replace("'","")
    string_to_clean = string_to_clean.replace('-','')
    string_to_clean = string_to_clean.replace('é','e')
    string_to_clean = string_to_clean.replace('è','e')
    string_to_clean = string_to_clean.replace('ê','e')
    string_to_clean = string_to_clean.replace('ô','o')
    string_to_clean = string_to_clean.replace('ï','i')
    string_to_clean = string_to_clean.replace('à', 'a')
    string_to_clean = string_to_clean.replace('ë', 'e')
    clean_string = string_to_clean.replace(' ', '')
    return clean_string

from datetime import datetime
import os.path
import re
import json
import mysqlx



IRAMUTEQ_SAVE_PATH = '/home/dleroux/Documents/corpus_iramuteq'
JSON_SAVE_PATH = '/media/dleroux/DATA/json_extraction'

class Converter () :

    def __init__(self, format, corpus_data):
        self.format = format
        self.corpus_data = corpus_data

class IramuteqConverter(Converter):

    def __init__(self, corpus_data):
         super().__init__("iramuteq", corpus_data)
         

    def save_to_iramuteq_txt_files(self):
            print('save to Iramuteq"')
            complete_path = os.path.join(IRAMUTEQ_SAVE_PATH, self.corpus_data.searched_word+".txt")
            corpus = ''
            for article in self.corpus_data.articles:
                if article is not None and article.id is not None:
                    corpus = corpus + self.to_iramuteq_txt(article)
            with open(complete_path, 'w') as txt_file:
                txt_file.write(corpus)
            
    def clean_balise_string(self, string_to_clean):
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
        return self.remove_unwanted_chars(clean_string)

    def to_iramuteq_txt(self, article):
        balises = self.create_iramuteq_balises(article)
        content = str(article.title) + '. ' + str(article.content)
        clean_content = re.sub('[^0-9A-Za-zçéèëêàâïîôùœŒÉ «»\(\)’;.?!%€\$,/:\-\']+','', content)
        text = balises + '\n' + clean_content + '\n' 
        return text

    def create_iramuteq_balises(self, article):
        text_balise = '****'
        author_balise = self.iramuteq_author_balise(article)
        date_balise = self.iramuteq_date_balise(article)
        id_balise = self.iramuteq_id_balise(article)
        thema_balise = self.iramuteq_thema_balise(article)
        tag_balise = self.iramuteq_tag_balise(article)
        return text_balise + ' ' + id_balise + ' ' + author_balise + ' ' + date_balise + ' ' + thema_balise + ' ' + tag_balise

    def iramuteq_author_balise(self, article):
        print(f'{article.id} {article._author} {article.title}')
        return '*author_'+ self.clean_balise_string(article.author)

    def iramuteq_date_balise(self, article):
        if article.date == 'no date':
            return '*date_nodate'
        date = datetime.strptime(article.date, '%d/%m/%Y')
        reverse_date = date.strftime('%Y%m')
        return '*date_' + reverse_date

    def iramuteq_id_balise(self, article):
        return '*id_'+ article.id

    def iramuteq_thema_balise(self, article):
        return '*thema_' + self.clean_balise_string(article.url.split('/')[1])

    def iramuteq_tag_balise(self, article):
        return '*tag_' + self.clean_balise_string(article.tag)

    def remove_unwanted_chars(self, string):
        return re.sub('[^a-zA-Z0-9_\*]','', string)
        


class JsonConverter(Converter):

    def __init__(self):
        super().__init__("json")
    
    def to_dict(self):
        return {self.searched_word : {article.id : article.to_dict() for article in self.articles}}

    def save_to_json(self):
        dump = self.dump_dict_to_json(self.to_dict())
        self.save_as_json_file(dump, self.searched_word)

    def dump_dict_to_json(self, json_dict):
        return json.dumps(json_dict, ensure_ascii= False, indent = 4)

    def save_as_json_file(self, json_res, searched_word):    
        complete_name = os.path.join(JSON_SAVE_PATH, searched_word +".json")
        with open(complete_name, "w+") as json_file:
            json_file.write(json_res)
    
    def to_dict(self):
        return {"title" : self.title, "url": self.url, "author": self.author, "date": self.date, "content": self.content}



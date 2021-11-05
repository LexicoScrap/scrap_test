
from requests import get
from scrapy import Selector

response = get("https://fr.wikipedia.org/wiki/Guerre_d%27Alg%C3%A9rie")
source = None 
if response.status_code == 200 :
    source = response.text

if source :
    selector = Selector(text=source)
    titles = selector.css("div.toc ul > li")
    for title in titles:
        level = title.css("span.tocnumber::text").extract_first()
        name = title.css("span.toctext::text").extract_first()
        print(level + " " + name)
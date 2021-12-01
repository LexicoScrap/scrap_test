


class Articles:

    def __init__(self, searched_word, max_size_result):
        self._searched_word = searched_word
        self._results = []
        self.articles = []
        self.max_size_result = max_size_result

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

    def print_article(self):
        print('-------------------------------------------------')
        print("article n°"+self.id)
        print("url: " + self.url)
        print("title: " + self.title)
        print("author: " + self.author)
        print("date: " + self.date)
        print("tag: " + self.tag)
        print("content: " + self.content)


from pprint import pprint
import feedparser
import os
from gnewsclient import gnewsclient
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import warnings
warnings.filterwarnings("ignore")

class SentimentAnalyse:

    def __init__(self, name):
        self.name = name
        self.sia = SentimentIntensityAnalyzer()
        self.custom_words = dict()
        self.article_list = []
        self.sentiment = float()
        self.gNews = gnewsclient()

        self._update_vader()

    def _update_vader(self):
        # read custom file dict lexicons
        self._read_custom_file()
        # read afinn-111 dict lexicons and combine them to update vader
        self.sia.lexicon.update({**self.__read_afinn(), **self.custom_words})

    def _read_custom_file(self, path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dicts', 'custom_words.txt'))):

        with open(path, 'r') as lexicon_file:
            for line in lexicon_file:
                (key, val) = line.split(':')
                self.custom_words[key] = float(val)

    @staticmethod
    def __read_afinn():
        d = {}
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dicts', 'AFINN-111.txt')), 'r') as afinn_file:
            for line in afinn_file:
                try:
                    (key, value) = line.split()
                    d[key] = float(value)
                except:
                    pass

        return d

    def __get_rss(self):
        data_feed = feedparser.parse('https://news.google.com/news/rss/search/section/q/'
                                     + self.name.replace(' ', '%20') + '%20cryptocurrency?ned=us&gl=US&hl=en')

        # pprint(data_feed)
        for article in data_feed['entries']:
            title = article['title']
            self.article_list.append(title)

        # pprint(self.article_list)

    def __get_rss_v2(self):
        self.gNews.query = self.name + ' Cryptocurrency'
        data = self.gNews.get_news()

        for article in data:
            self.article_list.append(article['title'])

    def _calculate_sentiment(self):
        try:
            for article in self.article_list:
                self.sentiment += self.sia.polarity_scores(article)['compound']
            self.sentiment /= len(self.article_list)
        except:
            self.sentiment = 0
    def get_sentiment(self):
        try:
            self.__get_rss_v2()
            self._calculate_sentiment()
        except:
            self.__get_rss()
            self._calculate_sentiment()

        return round(self.sentiment, 6)




if __name__ == '__main__':
    obj = SentimentAnalyse('Bitcoin Cash')
    print(obj.get_sentiment())

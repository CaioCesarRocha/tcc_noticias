import gensim, nltk, re, json, os, pymongo
from gensim import corpora,similarities, models
from nltk.tokenize import word_tokenize
from datetime import date, datetime
from scrapy import settings

FILTER_ONE_WEEK = 7
format="%d/%m/%Y"

class DataProcess(object):

    @staticmethod
    def date_filter(dateNews):
        today = date.today()
        return abs((today - dateNews).days)

    @staticmethod
    def open_file(name_file, notices, format="%d/%m/%Y"):
        with open(name_file,'r') as file:
            for line in file:
                notice = json.loads(line)
                if notice['corpo'] and notice['corpo'] != '':
                    notice['data'] = datetime.strptime(notice['data'],format).date()
                    notices.append(notice)

    @staticmethod
    def date_start(dateNews):
        start = date.fromordinal(dateNews.toordinal() - FILTER_ONE_WEEK)
        #start = start.strftime('%d/%m/%Y')
        start = datetime(start.year, start.month, start.day)
        return start

    @staticmethod
    def date_end(dateNews):
        end = date.fromordinal(dateNews.toordinal() + FILTER_ONE_WEEK)
        #end = end.strftime('%d/%m/%Y')
        end = datetime(end.year, end.month, end.day)
        return end




    


    

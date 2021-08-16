import json, re, pymongo, os
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from unidecode import unidecode
from nltk.corpus import stopwords  
from nltk.tokenize import word_tokenize
from datetime import date, datetime
from scrapy import settings

format="%d/%m/%Y"


class NoticiasPipeline:
	def process_item(self, item, spider):
		return item

class DropFaultDataPipeline:
	def process_item(self, item, spider):
		if item['data']:
			return item				   					
		else:
			raise DropItem("Missing data in %s" % item)

class DropFaultCorpoPipeline:
	def process_item(self, item, spider):
		if item['corpo']:
			return item
		else:
			raise DropItem("Missing corpo in %s" % item)

class DropNotCovid19:
	def process_item(self, item, spider):
		if (re.search("covid", item['corpo']) or re.search("vacina", item['corpo']) or re.search("doses", item['corpo']) or re.search("cloroquina", item['corpo']) or re.search("cpi", item['corpo']) ):
			return item
		else:
			raise DropItem("Is not notice about Covid-19")

class LowerPipeline:
	def process_item(self, item, spider):
		item['corpo'] = item['corpo'].lower()
		return item
        
class TagsSpecialsCorpoPipeline:
	def process_item(self,item,spider):
		str1 = item['corpo']
		str1 = unidecode(str1)
		str1 = re.sub('["\'\-,;%\[\]\{\}.*:@#?!&$\(\)/|]', ' ', str1)
		item['corpo'] = str1
		return item

class RemoveStopwordsPipeline:
	def process_item(self,item,spider):
		text = item['corpo']
		stop_words = set(stopwords.words('portuguese'))
		word_tokens = word_tokenize(text)
		filtered_text = [w for w in word_tokens if not w in stop_words]
		filtered_text = []
		for w in word_tokens:
		    if w not in stop_words:
		        filtered_text.append(w)
		item['corpo'] = filtered_text
		return item

class ProcessedCorpoPipeline:
	def process_item(self,item,spider):
		processed_corpo = DataUtility.pre_processing(item['corpo'])
		item['corpo'] = processed_corpo

class MongoDBPipeline:
	collection_name = 'notices_collection'
	#collection_name = 'teste'

	def __init__(self, mongo_uri, mongo_db):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'crawler')
			)

	def open_spider(self,spider):
		#self.client = pymongo.MongoClient(self.mongo_uri)
		self.client = pymongo.MongoClient("your_url_database")	
		self.db = self.client[self.mongo_db]

	def close_spider(self,spider):
		self.client.close()

	def process_item(self,item,spider):
		link = item['link']
		title = item['title']
		data = item['data']
		corpo = item['corpo']
		data = datetime.strptime(data,format).date()

		self.db[self.collection_name].insert_one({
			'link': link,
			'title': title,
			'data': datetime(data.year, data.month, data.day),
			'corpo': corpo
		})

		return item

		




    
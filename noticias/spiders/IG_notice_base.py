import scrapy, re
from w3lib.html import remove_tags
from noticias.items import NoticiasItem

class IG_Base_Spider(scrapy.Spider):
	name = 'IGNoticeBase'

	custom_settings = {
	    'ITEM_PIPELINES': {
	        'scrapy.pipelines.files.FilesPipeline': 1,	        
	        'noticias.pipelines.LowerPipeline' : 200,
	        'noticias.pipelines.TagsSpecialsCorpoPipeline': 305,
	        'noticias.pipelines.RemoveStopwordsPipeline': 310,
	    }
	}

	def __init__(self, notice_base=None, *args, **kwargs):
		super(IG_Base_Spider, self).__init__(*args, **kwargs)
		self.start_urls = [notice_base]

	def parse(self, response):
		text_with_tags = response.css("div#noticia p").extract()
		text_with_tags = ' '.join(text_with_tags)
		text_without_tags = remove_tags(text_with_tags)

		date = response.css('time::text').get()
		if date:
			date = date.split()[0]
		else:
			date = None

		link = response.url
		title = response.css('h1::text').get()
		data = date
		corpo = text_without_tags

		notice = NoticiasItem(link=link, title=title, data=data, corpo=corpo)
		yield notice
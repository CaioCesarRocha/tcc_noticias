import scrapy, re
from w3lib.html import remove_tags, remove_tags_with_content
from noticias.items import NoticiasItem

class Terra_Base_Spider(scrapy.Spider):
	name = 'TerraNoticeBase'

	custom_settings = {
	    'ITEM_PIPELINES': {
	        'scrapy.pipelines.files.FilesPipeline': 1,
	        'noticias.pipelines.DropFaultDataPipeline' : 150,
	        'noticias.pipelines.LowerPipeline' : 200,
	        'noticias.pipelines.TagsSpecialsCorpoPipeline': 305,
	        'noticias.pipelines.RemoveStopwordsPipeline': 310,
	    }
	}

	def __init__(self, notice_base=None, *args, **kwargs):
		super(Terra_Base_Spider, self).__init__(*args, **kwargs)
		self.start_urls = [notice_base]

	def parse(self, response):
		text = response.css("div.article__content--body p.text").extract()
		if(text == []):
			text = response.css("div.article__content--body p").extract()
		text = ' '.join(text)
		text_without_content_tags = remove_tags_with_content(text, ('script', ))
		text_without_tags = remove_tags(text_without_content_tags)

		date = response.css("div.date span::text").extract()
		date.pop(2)
		date =  ' '.join(date).split()
		date = "/".join(date)
		date = re.sub('jan', '01',str(date))
		date = re.sub('fev', '02',str(date))
		date = re.sub('mar', '03',str(date))
		date = re.sub('abr', '04',str(date))
		date = re.sub('mai', '05',str(date))
		date = re.sub('jun', '06',str(date))
		date = re.sub('jul', '07',str(date))
		date = re.sub('ago', '08',str(date))
		date = re.sub('set', '09',str(date))
		date = re.sub('out', '10',str(date))
		date = re.sub('nov', '11',str(date))
		date = re.sub('dez', '12',str(date))

		link = response.url
		title = response.css("h1::text").get()
		data = date
		corpo = text_without_tags

		notice = NoticiasItem(link=link, title=title, data=data, corpo=corpo)
		yield notice
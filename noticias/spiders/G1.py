import scrapy, re
from w3lib.html import remove_tags
from noticias.items import NoticiasItem


class G1Spider(scrapy.Spider):
	name = 'G1'
	allowed_domains = ['g1.globo.com']
	start_urls = ['https://g1.globo.com/bemestar/coronavirus/']

	custom_settings = {
        'ITEM_PIPELINES': {
        	'scrapy.pipelines.files.FilesPipeline': 1,
    		'noticias.pipelines.DropFaultDataPipeline' : 150,
    		'noticias.pipelines.LowerPipeline' : 200,
    		'noticias.pipelines.TagsSpecialsCorpoPipeline': 305,
    		'noticias.pipelines.RemoveStopwordsPipeline': 310,
            'noticias.pipelines.MongoDBPipeline': 350,
        }
    }

	def parse(self, response):
		for url in response.css("div.bastian-feed-item"):
								#div._ee
		    link = url.css('a::attr(href)').get()
		    yield response.follow(link, self.parse_next)        

	def parse_next(self, response):
		article_corpo = []
		for texts in response.css("div.mc-column.content-text"):
		    text_with_tags = texts.css("div.mc-column.content-text").get()
		    text_without_tags = remove_tags(text_with_tags)
		    article_corpo.append(text_without_tags.strip())
		article_corpo = ''.join(article_corpo)

		date = response.css('time::text').get()
		if date:
			date = date.split()[0]
		else:
			date = None

		corpo = article_corpo
		data = date
		link = response.url
		title = response.css('div.title h1::text').get()
					
		notice = NoticiasItem(link=link, title=title, data=data, corpo=corpo)
		yield notice
    	

		
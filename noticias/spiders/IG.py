import scrapy, re
from w3lib.html import remove_tags
from noticias.items import NoticiasItem

class IGSpider(scrapy.Spider):
	name = 'IG'
	allowed_domains = [ 'saude.ig.com.br', 'ultimosegundo.ig.com.br']
	start_urls = ['https://www.ig.com.br/']

	custom_settings = {
	    'ITEM_PIPELINES': {
	        'scrapy.pipelines.files.FilesPipeline': 1,
	        'noticias.pipelines.DropFaultDataPipeline' : 150,	        
	        'noticias.pipelines.LowerPipeline' : 175,
	        'noticias.pipelines.DropNotCovid19' : 200,
	        'noticias.pipelines.TagsSpecialsCorpoPipeline': 305,
	        'noticias.pipelines.RemoveStopwordsPipeline': 310,
	        'noticias.pipelines.MongoDBPipeline': 350,
	    }
	}

	def parse(self, response):
		linksH2 = response.css('h2 a::attr(href)').extract()
		for link in linksH2:
			yield response.follow(link, self.parse_next)
		linksDIV = response.css('div.linksRelacionados a::attr(href)').extract()
		for link in linksDIV:
			yield response.follow(link, self.parse_next)
		linksLI = response.css('li.chamada-secundaria a::attr(href)').extract()
		for link in linksLI:
			yield response.follow(link, self.parse_next)

	def parse_next(self, response):
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
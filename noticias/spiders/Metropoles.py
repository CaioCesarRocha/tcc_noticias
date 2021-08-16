import scrapy, re
from w3lib.html import remove_tags, remove_tags_with_content, replace_escape_chars
from noticias.items import NoticiasItem

class MetropolesSpider(scrapy.Spider):
    name = 'Metropoles'
    allowed_domains = ['metropoles.com']
    start_urls = ['https://www.metropoles.com/tag/coronavirus', 'https://www.metropoles.com']

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

    	for article in response.css("article"): 
    		link = article.css("a::attr(href)").extract_first()

    		yield response.follow(link, self.parse_next)

    def parse_next(self, response):
        try:
            article =  remove_tags_with_content(response.css("div.column article").extract_first(),which_ones=('div','div.twitter-tweet','figure','h6','script'))
        except:
            article =  remove_tags_with_content(response.css("div.column article").extract_first(),which_ones=('div','figure','script'))

        article = remove_tags(article)
        article = replace_escape_chars(article, which_ones = ('\n'))
        article = re.sub(r'http\S+','', article).strip()

        date = response.css('time::text').get()
        if date:
            date = date.split()[0]
        else:
            date = None

        link = response.url
        data = date
        title = response.css("h1::text").get()
        corpo = article   	  	

        notice = NoticiasItem(link=link, title=title, data=data, corpo=corpo)
        yield notice
        
        

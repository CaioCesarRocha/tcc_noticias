import scrapy,re
import w3lib.html
from w3lib.html import remove_tags, remove_tags_with_content, replace_escape_chars
from noticias.items import NoticiasItem

class UolSpider(scrapy.Spider):
    name = 'Uol'
    allowed_domains = ['uol.com.br']
    start_urls = ['https://noticias.uol.com.br/coronavirus/']

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
    	for url in response.css('div.thumbnails-wrapper'):
    	    link = url.css('a::attr(href)').get()
    	    yield response.follow(link, self.parse_next)

    def parse_next(self, response):
        have_embed = response.css("div.text div.instagram-embed").extract_first()
        have_embed = response.css("div.text div.twitter-embed").extract_first()
        have_embed = response.css("div.text div.slot-m").extract_first()
        have_embed = response.css("div.text div.gallery-embed").extract_first()
        
        if have_embed:
            article = ''.join(response.css("div.text p::text").extract())
        else:
            try:
                article = remove_tags_with_content(response.css("div.text").extract_first(),which_ones=('ul','li','style',))
                article = remove_tags(article)
                article = replace_escape_chars(article, which_ones = ('\n'))
                article = re.sub(r'http\S+','', article).strip()
                article = re.sub(r'instagram','',article).strip()
                article = re.sub(r'imagem','',article).strip()
            except: 
                article = remove_tags_with_content(response.css("div.text").extract_first(),which_ones=('div.slot-m','div.gallery-embed','div#playerInArticle','div.album-embed','style','div.twitter-embed', 'div.instagram-embed',))
                article = remove_tags(article)
                article = replace_escape_chars(article, which_ones = ('\n'))
                article = re.sub(r'http\S+','', article).strip()
                article = re.sub(r'instagram','',article).strip()
                article = re.sub(r'imagem','',article).strip()           

        date = response.css('div.author p.p-author.time::text').get()
        if date:
            date = date.split()[0]
        else:
            date = None

        link = response.url
        title = response.css('h1 span i::text').get()
        data = date
        corpo = article

        notice = NoticiasItem(link=link, title=title, data=data, corpo=corpo)
        yield notice      

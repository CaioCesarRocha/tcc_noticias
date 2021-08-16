import scrapy


class NoticiasItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    data = scrapy.Field()
    corpo = scrapy.Field()
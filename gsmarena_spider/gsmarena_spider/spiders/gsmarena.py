from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from .gsmarena_parser import ProductParser


class GsmarenaSpider(CrawlSpider):
    name = 'gsmarena-crawl'
    allowed_domains = ['www.gsmarena.com']
    start_urls = ['https://www.gsmarena.com/']        

    parse_spider = ProductParser()

    listings_css = [
        '.brandmenu-v2 li'
    ]

    products_css = [
        '.section-body li'           
    ]


    listings_le = LinkExtractor(restrict_css=listings_css)

    rules = (
        Rule(LinkExtractor(restrict_css=products_css), callback='parse_item'),
    )

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
    }

    def parse_start_url(self, response):
        self.parse_spider.brands = response.css('.brandmenu-v2 li ::text').getall()
        for link in self.listings_le.extract_links(response):
            yield response.follow(link.url, callback=self.parse)
    
    def parse_item(self, response):
        yield self.parse_spider.parse(response)        

import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SocalItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BlogSpider(scrapy.Spider):
    name = 'blog'
    start_urls = ['https://www.banksocal.com/resources/blog/']
    ITEM_PIPELINES = {
        'blog.pipelines.SocalPipeline': 300,

    }
    def parse(self, response):
        links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_post)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_post(self, response):
        date = response.xpath('//time/@datetime').get()
        title = response.xpath('//h1/text()').get()
        content = response.xpath('//section[@class="entry-content cf"]//text()[not (ancestor::p[@class="byline entry-meta vcard"] or ancestor::div[@class="wp-caption aligncenter"])]').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=SocalItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()

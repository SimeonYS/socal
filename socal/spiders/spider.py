import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SocalItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class SocalSpider(scrapy.Spider):
	name = 'socal'
	start_urls = ['https://www.banksocal.com/about-us/news/']

	def parse(self, response):
		articles = response.xpath('//li[@class="single-news_article"]')
		for article in articles:
			date = article.xpath('.//p/text()').get()
			post_links = article.xpath('.//a[@class="brand"]/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):

		title = response.xpath('//h1/text()').get()
		content = response.xpath('//article[@role="article"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SocalItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import IpbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class IpbSpider(scrapy.Spider):
	name = 'ipb'
	start_urls = ['https://www.lpb.dk/Hjaelp-og-Raadgivning/Nyheder?p=1']

	def parse(self, response):
		articles = response.xpath('//div[@class="news-inner"]')
		for article in articles:
			date = article.xpath('.//span[@class="dtstart"]/text()').get()
			post_links = article.xpath('.//a[@class="url"]/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@class="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response,date):

		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="col-sm-8 left-column main-content"]/p//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=IpbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

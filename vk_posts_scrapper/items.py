# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VkPostsScrapperItem(scrapy.Item):
    text = scrapy.Field(serializer=str)
    videos = scrapy.Field(serializer=list)
    video_urls = scrapy.Field(serializer=list)
    post_url = scrapy.Field(serializer=str)
    media = scrapy.Field(serializer=list)
    image_urls = scrapy.Field(serializer=list)
    images = scrapy.Field(serializer=list)
    screenshot = scrapy.Field(serializer=str)
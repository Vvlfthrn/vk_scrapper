import json

import lxml.html
import scrapy

from os import path
from typing import Iterable


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scrapy import Request
from scrapy_selenium import SeleniumRequest

from request import ModifiedSeleniumRequest
from vk_posts_scrapper.items import VkPostsScrapperItem
from vk_posts_scrapper.conditions import images_loaded


class VkSpiderSpider(scrapy.Spider):
    name = "vk_spider"
    base_url = 'https://vk.com'

    def __init__(self, group:str=None, posts_count:int=None, last_post:int=None, *args, **kwargs):
        assert group is not None, 'You must define vk group to parse'
        assert any([posts_count, last_post]), ('You must define posts_count or last_post '
                                                           'values to break parse procedure')
        super().__init__(*args, **kwargs)
        self.last_post = int(last_post)
        self.group = group
        self.posts_count = int(posts_count)

    def start_requests(self) -> Iterable[Request]:
        url = f"https://vk.com/wall-{self.group}?own=1"
        yield SeleniumRequest(url=url, callback=self.parse, cb_kwargs={'post_id': 0, 'posts_count': 0})

    def get_break(self, post_id, post_count):
        # can finish parsing
        return post_id <= self.last_post or post_count >= self.posts_count

    def parse(self, response, post_id:int = 0, posts_count:int = 0):
        posts = sorted([x.attrib["data-post-id"] for x in response.css(f'.post[id^="post-{self.group}"]')], reverse=True)
        for post_url in posts:
            post_id: int = int(post_url.split('_')[1])
            if self.get_break(post_id, posts_count):
                break
            image_css_selector = (f'[id^="post{post_url}"] .vkuiRootComponent__host [class^="vkitMediaGridItem__root"] '
                                  f'[class^="vkitMediaGridImage__image"], '
                                  f'[id^="post{post_url}"] [class^=vkitImageSingle__image]')
            restriction_text_selector = f'[id^="post{post_url}"] [class^=vkitRestrictionText__text]'

            single_page_video_selector = f'[id^="post{post_url}"] div.videoplayer_media video.videoplayer_media_provider'

            text_page_selector = f'[id^="post{post_url}"] [class^="vkitPostText__root"]'

            selectors = f'{restriction_text_selector}, {image_css_selector}, {single_page_video_selector}, {text_page_selector}'
            wait_to_load_selectors = f'{restriction_text_selector}, {image_css_selector}, {single_page_video_selector}'

            yield ModifiedSeleniumRequest(
                url=f'{self.base_url}/wall{post_url}',
                callback=self.post_detail_parse,
                cb_kwargs={'post_url': post_url},
                screenshot=True,
                source_code=True,
                wait_until=EC.all_of(
                    EC.presence_of_all_elements_located((
                        By.CSS_SELECTOR,
                        selectors)),
                    images_loaded((By.CSS_SELECTOR, wait_to_load_selectors))
                ),
                wait_time=30
            )
            posts_count += 1
            if self.get_break(post_id, posts_count):
                break
        if not self.get_break(post_id, posts_count):
            # next page
            yield SeleniumRequest(
                url=f'https://vk.com/wall-{self.group}?own=1&offset={posts_count}',
                callback=self.parse,
                cb_kwargs={'post_id': post_id, 'posts_count': posts_count}
            )

    def post_detail_parse(self, response, post_url:str=None):

        post = response.css(f'[id^="post{post_url}"]')[0]
        text = post.css('[class^="vkuiDiv"] [class^="vkuiDiv"] [class^="vkitShowMoreText__text"]::text').getall()
        media: list = post.css('[class^="vkitMediaGridItem__root"] a::attr(href)').getall()
        media.extend(
            post.css(
                '[class^="vkitPrimaryAttachment__root"] '
                'a[class^="vkitInteractiveWrapper__root"]::attr(href)').getall()
        )
        media.extend(
            post.css('div.VideoPrimaryAttachment__thumbWrapper a::attr(href)').getall()
        )

        item = VkPostsScrapperItem()
        root = lxml.html.fromstring(response.meta['source_code'])
        try:
            item['json_data'] = json.loads(root.find_class('PostContentContainer')[0].get('data-exec'))
        except json.JSONDecodeError:
            item['json_data'] = None
        item['text'] = text
        item['video_urls'] = set([x.split('?')[0] for x in media if 'video' in x])
        item['videos'] = []
        item['images'] = []
        item['image_urls'] = []
        item["post_url"] = post_url
        item["media"] = media
        item['screenshot'] = "screenshot" + post_url + ".png"
        item['post_date'] = item['json_data']['PostContentContainer/init']['item']['date'] if item['json_data'] else None
        with open(f'{path.join(self.settings["IMAGES_STORE"], "screenshot"+post_url+".png")}', 'wb') as f:
            f.write(response.meta['screenshot'])
        yield item

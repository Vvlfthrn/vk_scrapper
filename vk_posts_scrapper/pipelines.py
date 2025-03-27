# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from os.path import normpath
from pathlib import PureWindowsPath


import yt_dlp
from scrapy.http.request import NO_CALLBACK
from scrapy.utils.defer import maybe_deferred_to_future
from scrapy_selenium import SeleniumRequest
from twisted.internet.defer import DeferredList
from yt_dlp import DownloadError

from vk_posts_scrapper import settings

class VkPostsScrapperPipeline:
    async def process_item(self, item, spider):
        requests = []
        for x in item['media']:
            if 'photo' in x:
                requests.append(SeleniumRequest(
                    url=spider.base_url + x,
                    callback=NO_CALLBACK
                ))
        deferreds = []
        for r in requests:
            deferred = spider.crawler.engine.download(r)
            deferreds.append(deferred)
        responses = await maybe_deferred_to_future(DeferredList(deferreds))
        for _, r in responses:
            url = r.css('#pv_photo img::attr(src)').extract_first()
            if url:
                item['image_urls'].append(url)
        return item


ydl_opts = {
    "outtmpl": f'{settings.VIDEOS_STORE}%(id)s.%(ext)s',
    }

class VkPostsScrapperVideoPipeline:
    async def process_item(self, item, spider):
        for x in item['video_urls']:
            try:
                url = spider.base_url + x
                loader = yt_dlp.YoutubeDL(params=ydl_opts)
                info = loader.extract_info(url)
                filename = PureWindowsPath(normpath(PureWindowsPath(
                    info['requested_downloads'][0]['filename']).as_posix())).as_posix()
                item['videos'].append(filename)
            except DownloadError:
                pass
        return item


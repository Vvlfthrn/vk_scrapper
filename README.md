# vk_scrapper

Simple vk group scrapper based on:

* [scrapy](https://github.com/scrapy/scrapy)
* [selenium](https://github.com/SeleniumHQ/Selenium)
* [yt_dlp](https://github.com/yt-dlp/yt-dlp)

# Installation and use:
    pip install -r requirements.txt
    scrapy crawl vk_spider -o json.json -a group=vk_group_id -a posts_count=max_posts_to_load -a last_post=last_post_to_load

# Attention
*Spider can`t get nonpublic media!*
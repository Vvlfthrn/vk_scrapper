from scrapy_selenium import SeleniumRequest


class ModifiedSeleniumRequest(SeleniumRequest):

    def __init__(self,
                 wait_time=None, wait_until=None, screenshot=False, script=None, source_code=None, *args, **kwargs):
        super().__init__(wait_time, wait_until, screenshot, script,*args, **kwargs)
        self.source_code = source_code

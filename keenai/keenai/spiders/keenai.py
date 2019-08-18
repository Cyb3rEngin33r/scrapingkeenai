from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from keenai.items import KeenaiItem, KeenaiEventsItem
from scrapy import FormRequest, Request
from scrapy.conf import settings
from datetime import datetime 
import json, os
import logging
from scrapy.exceptions import CloseSpider

class keenaiSpider(CrawlSpider):
    name = 'keenaiPipeline'
    allowed_domains = ['app.keenai.com', "api.keenai.com"]
    start_urls = ['https://app.keenai.com/login']
    handle_httpstatus_list = [404]
    api_url = "https://api.keenai.com"
    auth_data = {}
    custom_setting = { "PASSWORD" : "me&myh0use" }
    base_dir = "./picdate"
     
    
    def parse_start_url(self, response):
        #print(self.settings.keys())
        post_data = { "name" : "", "username": settings['USER_NAME'], "password": settings['USER_PASSWORD'], "remember": "off"}
        login_url = "https://app.keenai.com/auth/login"

        return FormRequest(url=login_url, formdata=post_data, callback=self.parse_login)

    def parse_login(self, response):
        if response.status == 404:
            logging.error("Login failed")
            raise CloseSpider()
        else:
            logging.info("Login successful")
        self.auth_data = json.loads(response.body_as_unicode())
        url = self.api_url + "/3/events"
        headers={"Authorization": self.auth_data["token_type"] + " " + self.auth_data["access_token"]}
        request = Request(url, headers=headers, callback=self.parse_events)
        return request

    def parse_events(self, response):
        jsondata = json.loads(response.body_as_unicode())
        jsonstr = json.dumps(jsondata, sort_keys=True, indent = 4).encode('utf-8')
        if not os.path.exists(os.path.expanduser(settings["DATA_PATH"])):
            os.makedirs(os.path.expanduser(settings["DATA_PATH"]))
            logging.info("creating Directory : %s" % os.path.expanduser(settings["DATA_PATH"]))
        f = open(os.path.join(os.path.expanduser(settings["DATA_PATH"]),"index.json"), "wb")
        f.write(jsonstr)
        f.close()
        for i in json.loads(response.body_as_unicode()):

            request= Request(self.api_url + "/3/events/" + str(i["id"]) + "/files", 
                    headers={"Authorization": self.auth_data["token_type"] + " " + self.auth_data["access_token"]}, 
                    callback=self.parse_files)
            request.meta['events'] = i
            request.meta["date"] = datetime.strptime(i["start_date"], "%Y-%m-%dT%H:%M:%S+00:00")
            yield request

    def parse_files(self, response):
        events = KeenaiEventsItem()
        events["url"] = response.url
        events["eventsdata"] = json.loads(response.body_as_unicode())
        events['events'] = response.meta['events']
        events['date'] = response.meta['date']
        return events





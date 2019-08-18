# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings
import os
import hashlib
import json
from scrapy import Request, crawler
from scrapy.exceptions import DropItem
import logging
from shutil import rmtree

class KeenaiPipeline(object):

    def __init__(self, crawler):
        self.crawler = crawler
        self.directories = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        if not os.path.exists(os.path.expanduser(settings["DATA_PATH"])):
            os.makedirs(os.path.expanduser(settings["DATA_PATH"]))
            logging.info("creating Directory : %s" % settings["DATA_PATH"])

    def close_spider(self, spider):
        deldirs = list(set(os.listdir(os.path.expanduser(settings["DATA_PATH"]))) - set(self.directories))
        deldirs.remove("index.json")
        for each in deldirs:
            logging.info("Removing Directory : %s" % each)
            rmtree(os.path.join(os.path.expanduser(settings["DATA_PATH"]), each))
                

    def process_item(self, item, spider):
        
        eventsdatajson = json.dumps(item['eventsdata'], sort_keys=True, indent = 4).encode('utf-8')
        path = os.path.join(os.path.expanduser(settings["DATA_PATH"]), item["date"].strftime("%Y-%m-%d"))
        self.directories.append(item["date"].strftime("%Y-%m-%d"))
        logging.info("Checking dit : %s" % path)
        if not os.path.exists(path):
            os.makedirs(path)

        f = open(path + "/pics.json", "wb")
        f.write(eventsdatajson)
        f.close()
 
        jsonfilenames = {}
        for items in item["eventsdata"]:
            jsonfilenames[items["name"]] = items

        dirfilenames = os.listdir(path)
        dirfilenames.remove('pics.json')

        for listitem in list(set(dirfilenames) - set(jsonfilenames.keys())):
            os.remove(os.path.join(path, listitem))
            logging.info("Deleteing file : %s" % os.path.join(path, listitem))

        for listitem in list( set(jsonfilenames.keys()) - set(dirfilenames) ):
            image = jsonfilenames[listitem]
            filename = path + "/" + image['name']
            if not os.path.exists(filename):
                request = Request(image['media'], callback=self.save_image)
                request.meta["name"] = image['name']
                request.meta['path'] = path
                self.crawler.engine.crawl(request, spider,)
        
        return item

    def save_image(self, response):
        filename = response.meta['path'] + "/" + response.meta['name']
        f = open(filename, "wb")
        f.write(response.body)
        f.close()
        

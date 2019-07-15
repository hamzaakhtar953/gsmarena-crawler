# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class Accessory(Item):
    name = Field()
    brand = Field()
    userreviews = Field()
    requests = Field()

    image_urls = Field()
    network = Field()
    launch = Field()

    body = Field()
    display = Field()
    platform = Field()
    memory = Field()

    main_camera = Field()
    selfie_camera = Field()

    sound = Field()
    comms = Field()
    features = Field()
    battery = Field()
    misc = Field()


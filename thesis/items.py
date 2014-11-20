#############################
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy as s

"""
Main Webpage class for initial exploration
"""
class WebPageItem(s.Item):
    title = s.Field()
    url = s.Field() # page url
    outLinks = s.Field() # a list of (href, anchor-text) pairs
    headers = s.Field() # Response.headers
    body = s.Field() # body text of page
    depth = s.Field() # how many layers away from root we are
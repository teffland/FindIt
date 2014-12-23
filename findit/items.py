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
    # file meta data
    url = s.Field() # page url
    depth = s.Field() # how many layers away from root we are
    target = s.Field() # boolean for whether this is a target page or not
    
    # webgraph info
    inLinks = s.Field() # a list of (href, anchor-text) pairs
    outLinks = s.Field() # a list of (href, anchor-text) pairs
    # filegraph info
    inFiles = s.Field() # inLinks with href as hashed filename
    outFiles = s.Field() # outLinks with href as hashed filename
    
    # webpage content
    title = s.Field() # title of page
    headers = s.Field() # Response.headers
    body = s.Field() # body text of page
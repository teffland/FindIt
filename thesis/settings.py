###############################
# -*- coding: utf-8 -*-

# Scrapy settings for thesis project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'thesis'

SPIDER_MODULES = ['thesis.spiders']
NEWSPIDER_MODULE = 'thesis.spiders'

#CONCURRENT_REQUESTS = 1
#DEPTH_LIMIT = 1
DEPTH_STATS_VERBOSE = True
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
LOG = 'INFO'

# ITEM PIPELINES
ITEM_PIPELINES = {
    'thesis.pipelines.DuplicatesPipeline': 100,
    'thesis.pipelines.JsonWriterPipeline': 1000,
}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'thesis (+http://www.yourdomain.com)'
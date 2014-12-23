###############################
# -*- coding: utf-8 -*-

# Scrapy settings for thesis project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'findit'

SPIDER_MODULES = ['findit.spiders']
NEWSPIDER_MODULE = 'findit.spiders'

#CONCURRENT_REQUESTS = 1
DEPTH_LIMIT = 8
DEPTH_STATS_VERBOSE = True
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
LOG = 'INFO'

# Make it crawl BFS
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

# ITEM PIPELINES
ITEM_PIPELINES = {
    'findit.pipelines.DuplicatesPipeline': 100,
    'findit.pipelines.JsonWriterPipeline': 1000,
}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'findit (+http://tomeffland.us)'
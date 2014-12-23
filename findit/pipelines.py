###############################
# -*- coding: utf-8 -*-
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
import hashlib
from scrapy.exceptions import DropItem

"""
* Pipeline to remove duplicate urls
"""
class DuplicatesPipeline(object):
    def __init__(self):
        self.data_dir = 'data/buffalo'
        files = os.listdir(self.data_dir)
        print "Files downloaded already: ",
        print files
        self.urls_seen = set(files) #files
        
    def process_item(self, item, spider):
        if item['url'] in self.urls_seen: 
            raise DropItem("Duplicate item found: %s" % item['url'])
        else:
            self.urls_seen.add(item['url'])
            return item

"""
* Pipeline to write WebPageItem to json file 
* One file per webpage with url as filename
* Serialization technique:
*  # OFF # '.' -> '-'
*  '/' -> '_'
"""
class JsonWriterPipeline(object):
    def __init__(self):
        self.data_dir = 'data/buffalo'
    
    def process_item(self, item, spider):
        #print "ITEM URL: " + item['url']
    
        # output content
        content = {key:item[key] for key in ['title','headers','body','target','url']}
        data = json.dumps(dict(content), indent=4) + "\n"
        prefix = ''
        suffix = '_content'
        if content['target']: prefix = 'T_'
        
        fname = self.make_url_filename(content['url'], prefix=prefix, suffix=suffix)
        file = open(fname, 'w')
        file.write(data)
        file.close()
        
        # output meta file
        meta = {key:item[key] for key in ['url','depth','target','inLinks','outLinks','inFiles','outFiles']}
        data = json.dumps(dict(meta), indent=4) + "\n"
        prefix = ''
        suffix = '_meta'
        if content['target']: prefix = 'T_'
        
        fname = self.make_url_filename(meta['url'], prefix=prefix, suffix=suffix)
        file = open(fname, 'w')
        file.write(data)
        file.close()
        
        return item
    
    # change url from example.edu/stuff to example.edu_stuff for a filename
    def make_url_filename(self, url, prefix=None, suffix=None):

        # use md5 hash hexdigest for filenames since some are too long
        url = hashlib.md5(url).hexdigest()
        #if target: url = 'T_'+url
        url = prefix+url+suffix
        print url
        return self.data_dir + '/' + url
        
"""
* FindIt pipeline class definitions
"""
import settings
import json
import os
from util import make_url_filename

class JsonWriterPipeline():
    """docstring for JsonWriterPipeline"""
    
    def __init__(self):
        self.data_dir = settings.DATA_DIRECTORY

    def process_item(self, item, spider):
        # output content
        content = {key:item[key] for key in ['url','title','html','target']}
        #print content['body']
        if content['html'] == u'None':
            print "No content found... skipping this item"
            return {'url': "ERROR: Bad File"}
        data = json.dumps(dict(content), indent=4) + "\n"
        prefix = ''
        suffix = '_content'
        if content['target']: prefix = 'T_'
        if content['url'] in spider.start_urls: prefix = 'S_'
        
        fname = make_url_filename(content['url'], prefix=prefix, suffix=suffix)
        file = open(fname, 'w')
        print 'Writing file: %s' % fname
        file.write(data)
        file.close()
        
        # output meta file
        meta = {key:item[key] for key in ['url','target','relevance','distances','inLinks','outLinks','inFiles','outFiles']}
        # get the filename for each link, marking target or source as necessary
        for link in meta['outLinks']:
            if link['url'] in spider.target_urls: prefix = "T_"
            elif link['url'] in spider.start_urls: prefix = "S_"
            else: prefix = ''
            try:
                meta['outFiles'].append(make_url_filename(link['url'], prefix=prefix))
            except UnicodeEncodeError:
                print "Non-ascii found in meta outlink... skipping the link"
        #meta['outFiles'] = [ self.make_url_filename(link['url']) for link in meta['outLinks'] ] # get the filename for each out link
        data = json.dumps(dict(meta), indent=4) + "\n"
        prefix = ''
        suffix = '_meta'
        if meta['target']: prefix = 'T_'
        print "url: %s" % meta['url']
        #print "start urls:", spider.start_urls
        if meta['url'] in spider.start_urls: 
            prefix = 'S_'
            print "Found root url %s " % meta['url']
            #raw_input('Found starting url')
       
        fname = make_url_filename(meta['url'], prefix=prefix, suffix=suffix)
        file = open(fname, 'w')
        print 'Writing file: %s' % fname
        file.write(data)
        file.close()
        
        return item
    


class DuplicatePipeline():
    """docstring for DuplicatePipeline"""
    
    def __init__(self):
        self.data_dir = settings.DATA_DIRECTORY
        files = os.listdir(self.data_dir)
        print "Files downloaded already: ",
        print files
        self.urls_seen = set(files) #files
        
    def process_item(self, item, spider):
        return item
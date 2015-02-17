"""
* FindIt pipeline class definitions
"""
import settings
import json
import os
import hashlib

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
        
        fname = self.make_url_filename(content['url'], prefix=prefix, suffix=suffix)
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
                meta['outFiles'].append(self.make_url_filename(link['url'], prefix=prefix))
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
       
        fname = self.make_url_filename(meta['url'], prefix=prefix, suffix=suffix)
        file = open(fname, 'w')
        print 'Writing file: %s' % fname
        file.write(data)
        file.close()
        
        return item
    
    # change url from example.edu/stuff to example.edu_stuff for a filename
    def make_url_filename(self, url, prefix='', suffix=''):
        # use md5 hash hexdigest for filenames since some are too long
        url = hashlib.md5(url).hexdigest()
        url = prefix+url+suffix   
        return self.data_dir + url


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
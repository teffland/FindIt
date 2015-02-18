"""
* Crawler definitions
"""
import util
import settings
import json
from bs4 import BeautifulSoup as bs


class train():
    """Training Data Gatherer Spider:
    """
    def __init__(self, domains=settings.ALLOWED_DOMAINS):
        self.name = 'gather_data'
        self.known_paths = json.load(open(settings.KNOWN_PATHS_LOC, 'r'))
        self.known_urls = set([ url for path in self.known_paths for url in path])
        self.start_urls = set([ path[0] for path in self.known_paths ])
        self.target_urls = set([ path[-1] for path in self.known_paths ])
        print "Targer URLS: ", self.target_urls
        self.allowed_domains = domains
        print "Initial starting set of urls from MarkIt recorded paths"
        print '   ', self.known_urls

    def parse(self, response, level):
        #print response.__dict__.keys()
        current_url=response.url
        extracted_links = [] # at the end of the parse, return all extracted links to add to the queue
        extracted_items = [] # at the end of the parse, return all extracted items to send down pipeline
        p = bs(response._content)
        p = util.remove_scripts_and_style(p) # get rid of style and script tags and their content
                                             # they also mess with json output
        # loop through all the hyperlinks, extracting the ones we like
        for l in p.find_all('a'):
            # if link doesn't have an href skip it
            try: 
                url = l['href']
                #print "link href: %s" % url
            except KeyError:
                #print "link with no href"
                continue
            # filter unwanted url types. Details in util.py
            url = util.make_canonical_url(url, current_url = current_url)
            if util.is_good_url(url, allowed_domains=self.allowed_domains):
                anchor_text = l.text # pull anchor text
                # make link dict
                link = {'url':url, 'text':l.text, 'level':level+1}
                #print "Extracted url: %s" % url
                extracted_links.append(link)

        # check if this was a designated target page 
        if response.url in self.target_urls: target = True
        else: target = False 

        try: # sometimes parsing fails and this can kill the crawl, so bail out on this item gracefully
            item = {#'headers':response.headers,
                    'url':response.url,
                    'title':p.title.string,
                    'target':target,
                    'html':unicode(p.html),
                    'relevance':0.001,
                    'distances':[],
                    'outLinks':extracted_links,
                    'inLinks':[],
                    'outFiles':[],
                    'inFiles':[]
                    }
            extracted_items.append(item)
        except:
            print "Page parsing error. returning an empty item to handle gracefully"

        return extracted_items
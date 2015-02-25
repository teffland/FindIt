"""
* Crawler definitions
"""
import util
import settings
import json
import numpy as np
from bs4 import BeautifulSoup as bs
import joblib


class Train():
    """Training Data Gatherer Spider:
    """
    def __init__(self, domains=settings.ALLOWED_DOMAINS):
        self.name = 'gather_data'
        self.known_paths = json.load(open(settings.KNOWN_PATHS_LOC, 'r'))
        self.known_urls = set([ url for path in self.known_paths for url in path if len(path) > 0])
        self.start_urls = set([ path[0] for path in self.known_paths if len(path) > 0])
        self.target_urls = set([ path[-1] for path in self.known_paths if len(path) > 0])
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

        return extracted_items, extracted_links


"""
* Test class
""" 
class Test():
    """Test Data Gatherer Spider:
    """
    def __init__(self, start_url=settings.TEST_START_URL, domains=settings.ALLOWED_DOMAINS):
        self.name = 'find_data'
        self.start_urls = [start_url]
        self.allowed_domains = domains
        # load in the regressors
        self.page_reg = joblib.load(settings.DATA_DIRECTORY+'../clf/page_pipe.pkl')
        self.url_reg = joblib.load(settings.DATA_DIRECTORY+'../clf/url_pipe.pkl')

    def parse(self, response, level):
        prev_page_rel = level # the previously predicted relevance from the link is passed in as the level
        p = bs(response._content)
        p = util.remove_scripts_and_style(p) # get rid of style and script tags and their content
        extracted_items = []
        extracted_links = []
        try :
            X = {'content':unicode(p.html),
                 'url':response.url,
                 'title':p.title.string}
            #print "Page X:", X
            page_prediction = self.page_reg.predict([ X ]) # need the data in list form
            print "Url predicted relevance: %0.4f, page predicted relevance: %0.4f for %s" % (prev_page_rel, page_prediction, response.url)
            if prev_page_rel >=.85 or page_prediction >= .85:
                raw = raw_input("Is this a course descriptions page? (y/yes/n/no): ")
                print "You input: ", raw
                if raw == "y" or raw == "yes":
                    item = {#'headers':response.headers,
                        'url':response.url,
                        'title':p.title.string,
                        'target':True,
                        'html':unicode(p.html),
                        'relevance':1.0,
                        'distances':[],
                        'outLinks':[],
                        'inLinks':[],
                        'outFiles':[],
                        'inFiles':[]
                    }
                    extracted_items.append(item)
                elif raw == "n" or raw == "no":
                    item = {#'headers':response.headers,
                        'url':response.url,
                        'title':p.title.string,
                        'target':False,
                        'html':unicode(p.html),
                        'relevance':0.01,
                        'distances':[],
                        'outLinks':[],
                        'inLinks':[],
                        'outFiles':[],
                        'inFiles':[]
                    }
                    extracted_items.append(item)

        except:
            print "Error1: Returning blank"
            return [], []
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
            url = util.make_canonical_url(url, current_url = response.url)
            if util.is_good_url(url, allowed_domains=self.allowed_domains):
                anchor_text = l.text # pull anchor text
                # make link dict
                link = {'url':url, 'text':l.text, 'level':0}
                #print "Extracted url: %s" % url
                extracted_links.append(link)
        # gains = list(page_prediction*np.ones(len(extracted_links)) - self.url_reg.predict(extracted_links))
        try:
            predictions = self.url_reg.predict(extracted_links)
            links = [ link['url'] for link in extracted_links ]
            url_predictions = sorted( zip(predictions, links), key=lambda x:x[0], reverse=True)
            better_urls = [ pred for pred in url_predictions if pred[0] > page_prediction - .25 ]
        except:
            print "Error2: Returning blank"
            return [], []

        return extracted_items, better_urls #url_predictions


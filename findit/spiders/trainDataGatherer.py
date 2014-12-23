###############################################
import scrapy as s
from bs4 import BeautifulSoup as bs
import json
from findit.items import WebPageItem

class trainDataGatherer(s.Spider):
    name = "gather_data"

    def __init__(self, domain="buffalo.edu", data="buffalo", *a, **kw):
        self.allowed_domains = [domain]
        self.start_urls = [ "http://www.buffalo.edu/academics.html" ]
        self.data_dir = 'data/'+data
        try:
            f = open(self.data_dir + '/target_urls.json', 'r')
        except FileNotFoundError:
            print "No target URLs specified, proceeding with no targets."
            self.target_urls = []
        #print f.readlines()
        data = json.load(f)
        self.target_urls = data['target_urls']
        # pick off target path ends as targets
        self.target_urls.append([path[-1] for path in data['target_paths']])
        self.target_paths = data['target_paths']
        self.targets_set = set([page for path in self.target_paths for page in path])
        
        print "Target URLs: ", self.target_urls
  
        super(trainDataGatherer, self).__init__(*a, **kw)
    
    def parse(self, response):
        # parse the page with bs4
        p = bs(response._body)

        # the page item
        page  = WebPageItem()
        links = []
        # mark target pages
        if response._url in self.target_urls: page['target'] = True
        else: page['target'] = False
        
        # standardize current page url
        current_url = self.make_canonical_url(response._url)
        
        # populate page data item
        page['url'] = current_url # add url to page object
        page['headers'] = response.headers
        page['body'] = response._body
        page['title'] = p.title.text
        page['depth'] = response.meta['depth']
        
        # loop through all the hyperlinks
        for l in p.find_all('a'):
            # if link doesn't have an href skip it
            try: 
                url = l['href']
            except KeyError:
                continue
            
            # standardize url
            url = self.make_canonical_url(url, current_url)
            
            # skip mailto addresses
            if self.is_mailto(url): continue
            # skip cyclic addresses
            if self.is_cyclic_url(url): continue
            
            # add url to urls list for item
            anchor_text = l.text  
            link = ( url , anchor_text )
            #print link
            links.append(link)
            
        page['outLinks'] = links
        # add in blank data items, these will get replaced later
        page['inLinks'] = []
        page['outFiles'] = []
        page['inFiles'] = []
        # serialize this page
        yield page
        
        # follow the outLinks
        for link in page['outLinks']:
            web_url = 'http://' + link[0]
            if web_url in self.targets_set: yield s.Request(web_url, callback=self.parse, priority=1)
            else: yield s.Request(web_url, callback=self.parse)
        
            
    """
    * Used to take a url as a string and make into canonical form for crawling
    * Canonical Rules:
    * * Always remove 'http://'  - This will be added back on when submitting a request if using internet
    * * Always remove trailing '/'
    """
    def make_canonical_url(self, url, current_url=None):
        # change local url to global
        if url != '' and url[0] == '/':
            url = current_url + url
        # remove transer protocol prefixes
        if 'https://' in url:
            url = url[8:]
        if 'http://' in url:
            url = url[7:]
        # remove trailing slash
        if url[-1] == "/":
            url = url[:-1]
        return url
    
    """
    * Detect cyclic url pattern
    * eg, url = a/b/c/d/e/c/d/e (we use this example for comments)
    *         is likely a repeating cycle of links that are valid or is a bot trap
    *         either way it won't yield any new content
    """
    def is_cyclic_url(self, url_str):
        # make sure url doesn't have trailing slash
        if url_str[-1] == '/': url_str = url_str[:-1]
        url = url_str.split('/')[::-1] # split into list and reverse order (eg, a/b/c = [c,b,a])
        potential_pattern = [url[0]] 
        for i in range(1,len(url)): # go backwards from second to last towards front
            offset =  len(potential_pattern) # size of potential pattern in unexplored prefix of url
            if offset >= len(url)/2: # the potential pattern length > half the url, so it can't repeat
                return False
            elif url[i:i+offset] == potential_pattern: # check for repeated pattern
                url = url[i:i+offset]
                url.reverse()
                print 'Repeating link pattern found: ', url, potential_pattern[::-1]
                return True
            else: # else char didn't match beginning of tail pattern
                potential_pattern.append(url[i]) # add to pattern (eg, tail = [e, d])
        return False
    
    """
    * Check if the address is a 'mailto' address
    """
    def is_mailto(self, url):
        if 'mailto' in url: return True
        else: return False
        
    
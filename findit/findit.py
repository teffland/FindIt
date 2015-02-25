#! /Users/thomaseffland/.virtualenvs/findit/bin/python
"""
* FindIt driver file
"""
import sys
import spiders
from scheduler import Scheduler
from Queue import PriorityQueue
import settings
import pipelines
import requests
from time import sleep
import random
import backlinks
import features

"""
==================================================================================
* Function definitions
==================================================================================
"""

"""
* Crawl Spider:
* params:
*   spider - the name of the spider class in spiders.py to use
* 
* The spider knows how to parse pages to return items and new urls to crawl
* The items are passed to through the pipelines
* The new urls are added to the queue at the specified level
"""
def crawl_spider(spider):
    ############### TRAIN SPIDER ##############
    if spider == "train":
        # initialize the scheduling queue
        q = Scheduler()              
        # initialize all of the pipelines
        pipeline = []
        for pipe in settings.PIPELINES:
            try:
                pipeline.append( getattr( pipelines, pipe )() )
            except: 
                print "Error: Unable to initialize %s pipe" % pipe
                quit()
        # initialize the spider
        # try:
        #     s = getattr(spiders, spider)()    
        # except:
        #     print "Error: It's likely that the input spider does not exist in spiders.py"
        #     quit()
        s = spiders.Train()
        #print s.__doc__
        # add all of the start links and known links to the top level of the queue
        for url in list(s.start_urls) + list(s.known_urls):
            q.add_link(url, 0)
        q.print_queue()
        # request urls while scheduler not empty and pass to to spider
        # add returned links to the queue
        # send returned items down the pipeline
        visits = 0
        while not q.is_empty():
            wait_between_requests() # wait a random small amount of time so we're less detectable
            url, level = q.get_next_link(what_level=True)
            print "Visit #%i, Q level %i, Q volume %i" % (visits, level, q.queue_volume())
            response = get_request(url)
            if response: 
                items, extracted_links = s.parse(response, level=level) # links and items are both links
                #print "exctracted links:", links
                add_to_queue(q, extracted_links) # manage the returned links
                send_down_pipeline(pipeline, items, s) # manage the returned items
                if settings.ASK_BETWEEN_REQUESTS: raw_input("Press ENTER to continue?")
                visits += 1 

        if q.is_empty(): print "CRAWL IS FINISHED: Queue is empty"
        #if visits >= settings.MAX_CRAWLS: print "CRAWL IS FINISHED: Crawled max number of urls (%i total)" % visits

    ################ TEST SPIDER ##############
    elif spider == "test":
        print "Test case"
        q = PriorityQueue()              
        queued_links = set()
        # initialize all of the pipelines
        pipeline = []
        for pipe in settings.PIPELINES:
            try:
                pipeline.append( getattr( pipelines, pipe )() )
            except: 
                print "Error: Unable to initialize %s pipe" % pipe
                quit()
        # initialize the spider
        # try:
        #     s = spiders.Test()    
        # except:
        #     print "Error: It's likely that the input spider does not exist in spiders.py"
        #     quit()
        #print s.__doc__
        s = spiders.Test()    
        # add all of the start links and known links to the top level of the queue
        q.put((-.1, s.start_urls[0]))
        queued_links.add(s.start_urls[0])
        # request urls while scheduler not empty and pass to to spider
        # add returned links to the queue
        # send returned items down the pipeline
        visits = 0
        while not q.empty():
            wait_between_requests() # wait a random small amount of time so we're less detectable
            priority, url = q.get()
            print "Q get:", -priority, url
            print "Visit #%i, Q volume %i" % (visits, q.qsize())
            response = get_request(url)
            if response: 
                items, extracted_links = s.parse(response, level=-priority) # links and items are both links
                # print "Extracted item: ",items
                #print "extracted links:", extracted_links
                #print "exctracted links:", links
                for link in extracted_links:
                    if link[1] not in queued_links:
                        # print link
                        q.put((-link[0], link[1]))
                        queued_links.add(link[1])
                    # else:
                        # print "We already queued %s" % link[1]
                send_down_pipeline(pipeline, items, s) # manage the returned items
                if settings.ASK_BETWEEN_REQUESTS: raw_input("Press ENTER to continue?")
                visits += 1 

        if q.empty(): print "CRAWL IS FINISHED: Queue is empty"
        #if visits >= settings.MAX_CRAWLS: print "CRAWL IS FINISHED: Crawled max number of urls (%i total)" % visits

    else:
        quit()




# get response from link with error handling
def get_request(url):
    try:
        response = requests.get(url)
    except:
        print "Could not receive response"
        return
    # response = requests.get(url)
    #print response.__dict__.keys()
    if response.status_code == 200:
        #print "Received OK response from url ", response.url
        return response
    else: print "Received NOT OK response from url ", response.url 

# take list of link dicts and pass add them to the queue
def add_to_queue(queue, links):
    for link in links:
        queue.add_link(link['url'], link['level'], check_visited=not settings.CRAWL_DUPLICATES)

# pass items down the pipeline
def send_down_pipeline(pipeline, items, spider):
    for item in items:
        for pipe in pipeline:
            item = pipe.process_item(item, spider)
        print "Item written: %s" % item['url']

# wait a small random amount of time to prevent sites from identifying bot activity
def wait_between_requests():
    wait = settings.WAIT_LENGTH
    random_wait = random.uniform( wait*.5, wait*1.5)
    # print "waiting %.3f seconds until next request" % random_wait
    sleep(random_wait)

# print help function
def print_help():
    help_text = """
    #############################################################################
    ##########################   FindIt Help   ##################################
    #############################################################################

        To crawl a spider use the command:
                python findit.py crawl <spider>

        To ask between crawl requests use the --ask flag after the spider name

        To create an inverted index of links use the command:
                python findit.py invert

        To calculate the relevance metric and optimal link paths use the command:
                python findit.py score

        To convert all the downloaded pages into their feature representations us the command:
                python findit.py featurize 

    #############################################################################
    """
    print help_text

"""
=======================================================================================
* Driver script
=======================================================================================
"""
if len(sys.argv) <= 1:    # no currently supported commands called
    print_help()
    quit()

elif len(sys.argv) in [2,3,4]:  # <command> 
    command = sys.argv[1]
    # crawl a spider
    if command == "crawl": 
        try:
            spider = sys.argv[2]
        except IndexError:
            print "Error: Please specify a spider from spiders.py"
        #try:
        #    if sys.argv[3] == "--ask": settings.ASK_BETWEEN_REQUESTS = True
        #except:
        crawl_spider(spider)
    # invert link index
    elif command == "invert": 
        backlinks.invert_links()
    # calculate the relevance score of all the data
    elif command == "score":
        backlinks.calculate_relevance_scores()
    # featurize all of the pages, creating all the training data
    #elif command == "featurize":
    #    features.featurize_all()

    # no correct command used
    else:
        print "Error: unsupported command used"
        print_help()
        quit()


else:                     # too many arguments 
    print_help()
    quit()
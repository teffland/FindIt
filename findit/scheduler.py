"""
* Findit crawl scheduling queue
"""
from collections import deque
from random import shuffle
from settings import MAX_CRAWLS

class Scheduler():
    """ docstring for Scheduler"""

    def __init__(self, levels=3):
        self.queue = [ deque([]) for i in range(levels)] # queue is [ known paths, path siblings, path cousins]
        self.visited_urls = set()
        self.queue_set = set()
        self.reached_max_crawls = False
        print "Scheduler Queue Initiated"

    # add a link to a subcontainer at the specified level
    def add_link(self, link, level, check_visited=True):
        self.update_queue_set()
        # set no more crawls flag if we add up to max crawl size
        # if (len(self.queue_set) + len(self.visited_urls)) >= MAX_CRAWLS: 
        if self.queue_volume() >= MAX_CRAWLS: 
            print "Max Queue size reached! No more crawling"
            self.reached_max_crawls = True
        if self.reached_max_crawls:
            #print "No more adding to queue"
            return
        if check_visited: 
            if link in self.visited_urls: 
                #print "The url %s has already been visited" % link
                return
            if link in self.queue_set:
                #print "The url %s is already in the queue" % link
                return
        try:
            self.queue[level].append(link)
        except IndexError:
            print "Error adding link to queue: subcontainer " + str(level) + " doesn't exist"

    # report back the next link from the lowest nonempty level
    def get_next_link(self, level=None, what_level=False):
        # return first from specified level
        if level:
            subcontainer = self.queue[level]
            if what_level:
                url = subcontainer.popleft()
                self.visited_urls.add(url) # keep the big list of what we've returned
                return url , l 
            else: 
                url = subcontainer.popleft()
                self.visited_urls.add(url) # keep the big list of what we've returned
                return url 

        # we didn't ask for a specific level, so return topmost
        l = 0 # keep track of levels
        for subcontainer in self.queue:
            if (len(self.visited_urls) % 25) == 0 : #every 25 visits, shuffle the subcountainers to mix up domains a bit
                print "Shuffling subcontainer"
                shuffle(subcontainer)
            if len(subcontainer) > 0:
                if what_level:
                    url = subcontainer.popleft()
                    self.visited_urls.add(url) # keep the big list of what we've returned
                    return url , l 
                else: 
                    url = subcontainer.popleft()
                    self.visited_urls.add(url) # keep the big list of what we've returned
                    return url 
            l += 1

    # find out if it's totally empty
    def is_empty(self):
        if self.queue_volume() == 0: return True
        else: return False

    # get total number of elements in queue
    def queue_volume(self):
        v = sum([ len(subcontainer) for subcontainer in self.queue ])
        #print "Queue Volume: ", v
        return v

    def update_queue_set(self):
        self.queue_set = set()
        for subcontainer in self.queue:
            self.queue_set ^= set(subcontainer ) #take the union of the sets
    
    def print_queue(self, level=None):
        if level: 
            try:
                print "Queue level %i:" % level
                print self.queue[level]
            except IndexError:
                print "Index Error: Queue level %i doesn't exist" % level
        else:
            print "Queue"
            print self.queue

class Priority():
    """ Docstring for priority Q """
    def __init__(self):
        self.queue = [ deque([]) for i in range(levels)] # queue is [ known paths, path siblings, path cousins]
        self.visited_urls = set()
        self.queue_set = set()
        self.reached_max_crawls = False
        print "Scheduler Queue Initiated"

    # add a link to a subcontainer at the specified level
    def add_link(self, link, level, check_visited=True):
        self.update_queue_set()
        # set no more crawls flag if we add up to max crawl size
        # if (len(self.queue_set) + len(self.visited_urls)) >= MAX_CRAWLS: 
        if self.queue_volume() >= MAX_CRAWLS: 
            print "Max Queue size reached! No more crawling"
            self.reached_max_crawls = True
        if self.reached_max_crawls:
            #print "No more adding to queue"
            return
        if check_visited: 
            if link in self.visited_urls: 
                #print "The url %s has already been visited" % link
                return
            if link in self.queue_set:
                #print "The url %s is already in the queue" % link
                return
        try:
            self.queue[level].append(link)
        except IndexError:
            print "Error adding link to queue: subcontainer " + str(level) + " doesn't exist"

    # report back the next link from the lowest nonempty level
    def get_next_link(self, level=None, what_level=False):
        # return first from specified level
        if level:
            subcontainer = self.queue[level]
            if what_level:
                url = subcontainer.popleft()
                self.visited_urls.add(url) # keep the big list of what we've returned
                return url , l 
            else: 
                url = subcontainer.popleft()
                self.visited_urls.add(url) # keep the big list of what we've returned
                return url 

        # we didn't ask for a specific level, so return topmost
        l = 0 # keep track of levels
        for subcontainer in self.queue:
            if (len(self.visited_urls) % 25) == 0 : #every 25 visits, shuffle the subcountainers to mix up domains a bit
                print "Shuffling subcontainer"
                shuffle(subcontainer)
            if len(subcontainer) > 0:
                if what_level:
                    url = subcontainer.popleft()
                    self.visited_urls.add(url) # keep the big list of what we've returned
                    return url , l 
                else: 
                    url = subcontainer.popleft()
                    self.visited_urls.add(url) # keep the big list of what we've returned
                    return url 
            l += 1

    # find out if it's totally empty
    def is_empty(self):
        if self.queue_volume() == 0: return True
        else: return False

    # get total number of elements in queue
    def queue_volume(self):
        v = sum([ len(subcontainer) for subcontainer in self.queue ])
        #print "Queue Volume: ", v
        return v

    def update_queue_set(self):
        self.queue_set = set()
        for subcontainer in self.queue:
            self.queue_set ^= set(subcontainer ) #take the union of the sets
    
    def print_queue(self, level=None):
        if level: 
            try:
                print "Queue level %i:" % level
                print self.queue[level]
            except IndexError:
                print "Index Error: Queue level %i doesn't exist" % level
        else:
            print "Queue"
            print self.queue
"""
* Findit settings for driver file
"""

KNOWN_PATHS_LOC = "../data/paths/big_agg_paths.json"
CRAWL_DUPLICATES = False # check to see if we've crawled already or not 
MAX_CRAWLS = 500
WAIT_LENGTH = .5# length in seconds to wait between requests, actual wait time varies from +-50% of this time
ASK_BETWEEN_REQUESTS = False #True # set True to pause between each requests (for analyzing output)
PIPELINES = [ 'JsonWriterPipeline'
            ]
DATA_DIRECTORY = "../data/all2/" #leave the trailing "/"
ALLOWED_DOMAINS = ["buffalo.edu",
                   "washington.edu",
                   "northwestern.edu", 
                   "rochester.edu",
                   "bu.edu",
                   "unc.edu",
                   "illinois.edu",
                   "umd.edu"
                    ]
TEST_START_URL = "http://rochester.edu"
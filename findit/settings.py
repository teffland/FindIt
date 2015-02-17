"""
* Findit settings for driver file
"""

KNOWN_PATHS_LOC = "../data/paths/agg_paths.json"
CRAWL_DUPLICATES = False # check to see if we've crawled already or not 
MAX_CRAWLS = 1000
WAIT_LENGTH = .5# length in seconds to wait between requests, actual wait time varies from +-50% of this time
ASK_BETWEEN_REQUESTS = False # set True to pause between each requests (for analyzing output)
PIPELINES = [ 'JsonWriterPipeline'
            ]
DATA_DIRECTORY = "../data/all_big/" #leave the trailing "/"
ALLOWED_DOMAINS = ["buffalo.edu", "washington.edu", "northwestern.edu"]
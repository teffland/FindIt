###########################
import os
import json
import sys

if len(sys.argv) == 2:
    data_dir = sys.argv[1]
else:
    print "ERROR: Please specify the directory to work on"
    quit()

files = [ file for file in os.listdir(data_dir) if file[:-5] == "_meta" ]

inlinks = {} #inlinks is essentially an inverted index of links
# get entire inverted index
print "Collecting outgoing links from:"
for fname in files:
    f = open(data_dir + '/' + fname, 'r')
    #print f.readlines()
    data = json.load(f)
    url = data['url']
    outlinks = data['outLinks']
    print url
    for link in outlinks:
        #print link
        try: 
            if url not in set(inlinks[link[0]]):
                inlinks[link[0]].append(url)
        except KeyError:
            inlinks[link[0]] = []
    f.close()
print "Writing back inLinks"
# write the relevant portion of the index back to each file
for fname in files:
    f = open(data_dir + '/' + fname, 'r+')
    data = json.load(f)
    url = data['url']
    data['inLinks'] = inlinks[url]
    #print json.dumps(data)
    f.seek(0)
    f.write(json.dumps(data))
    f.truncate()
    f.close()
#print inlinks.values()
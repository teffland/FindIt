"""
* BackLink Data Gathering Script
* Essentially creates an inverted index on all links between pages
"""
import os
import json
import settings
import tree
from collections import deque

def invert_links():
    data_dir = settings.DATA_DIRECTORY
    files = [ file for file in os.listdir(data_dir) if file[-5:] == "_meta" ]

    inlinks = {} #inlinks is essentially an inverted index of links
    infiles = {} # correspongding filename hashes for inlinks
    # get entire inverted index
    print "Collecting outgoing links from %s" % data_dir
    for fname in files: # for each page
        # strip the prefix and suffix from the filename
        #if 'T_' in fname: fhash = fname[2:-5]
        #else: fhash = fname[:-5]
        fhash = fname[:-5]
        #print "fhash: %s" % fhash
        # load in the file
        f = open(data_dir + '/' + fname, 'r')
        #print f.readlines()
        data = json.load(f)
        url = data['url']
        outlinks = data['outLinks']
        outfiles = data['outFiles']
        if len(outlinks) != len(outfiles): print "ERROR: Number of outlinks and outfiles mistmatch"
        # calculate the inlinks and infiles
        for link, file in zip(outlinks, outfiles): # for each link on that page
            # strip the file name off of the directory
            # index all of the inlinks
            link['source'] = url # we want to know where the link came from
            try: 
                if link not in inlinks[link['url']]: # if link not already in inlinks list
                    inlinks[link['url']].append(link) # add to the inlink list
            except KeyError:
                inlinks[link['url']] = [link]   # if we haven't created an inlinks list for this link yet, do it
            #print "url: %s\n link: %s, inlinks[link.url']: %s" % (url, link, inlinks[link['url']])
            #raw_input("Continue?")
            # index the infiles
            #print file
            file = file.split('/')[-1] # strip the directory from the file name
            #print file
            try: 
                if fhash not in infiles[file]: # if link not already in inlinks list
                    infiles[file].append(fhash) # add to the inlink list
            except KeyError:
                infiles[file] = [fhash]   # if we haven't created an inlinks list for this link yet, do it


        f.close()
    print "Writing back inLinks and inFiles"
    # write the relevant portion of the index back to each file
    errorcount = 0
    for fname in files:
        # strip the prefix and suffix from the filename
        #if 'T_' in fname: fhash = fname[2:-5]
        #else: fhash = fname[:-5]
        fhash = fname[:-5]
        # open the datum file
        f = open(data_dir + '/' + fname, 'r+')
        data = json.load(f)
        url = data['url']
        try:
            data['inLinks'] = inlinks[url]
        except KeyError: # somehow this file never had a link lead to it, so complain about it but just leave it's inlinks blank
            print """ERROR: %s was never lead to by another page """ % url
            errorcount += 1
            f.close()
            continue
        try:
            data['inFiles'] = infiles[fhash]
            #print "infiles: ", infiles[fhash]
        except KeyError: # somehow this file never had a link lead to it, so complain about it but just leave it's inlinks blank
            print """ERROR: no infiles found """
            f.close()
            continue
        # go to beginning of file and rewrite out it's data with changes
        f.seek(0)
        f.write(json.dumps(data, indent=4))
        f.truncate()
        f.close()
    print "Number of NoInLink errors: %i / %i" % (errorcount, len(files))
    #print inlinks.values()


"""
* Calculate the relevance scores for each page as a function of their link distance from a target page
*  We trace the path from a target to the source using BFS
*  Since each page may lie on more than one target-source optimal path, 
    we will average its distances which lie on such a path
*  The relevance = max(1 - minDistanceFromTarget/sourceDistanceFromTarget, .01)
"""
def calculate_relevance_scores():
    data_dir = settings.DATA_DIRECTORY
    files = [ file for file in os.listdir(data_dir) if file[-5:] == "_meta" ]
    targets = [ file for file in files if file[:2] == "T_"]
    sources = [ file for file in files if file[:2] == "S_"]
    print "Calculating relevance scores"
    print "Targets: ", targets
    print "Sources: ", sources
    # for each target page, trace back the optimal path to the source
    for fname in targets:
        # label the target
        print "On target file %s" % fname
        f = open(data_dir + fname, 'r+')
        data = json.load(f)
        data['relevance'] = 1.0
        f.seek(0)
        f.write(json.dumps(data, indent=4))
        f.truncate()
        f.close()
        target_nodename = fname[:-5]
        print target_nodename
        # BFS to source from this target
        Q = deque([ (datum, target_nodename) for datum in data['inFiles'] ]) # BFS queue
        V = set([target_nodename]) # Set of queued and visited urls
        T = tree.Tree() # BFS Tree
        T.add_node(target_nodename, data)
        source = None
        print "Building target-source path tree"
        while Q: # go until bfs queue is empty or we find the source node                print "Q: ", Q
            nodename, parent = Q.popleft() # get the next node and parent
            print "Node: %s, parent: %s" % (nodename, parent)
            print "Q size: %i, V size: %i" % (len(Q), len(V))
            nodefile = open(data_dir + nodename+"_meta" , 'r')
            nodedata = json.load(nodefile) # was load(f) <- incorrect
            T.add_node(nodename, nodedata, parent=parent)
            # if we find a source node, then we have constructed as much of the BFS tree as we need
            if (nodename+'_meta') in sources: 
                source = T.nodes[nodename]
                print "Found source!"
                break
            # add each infile to the queue
            for infile in (f for f in nodedata['inFiles'] if f not in V):
                V.add(infile) # add this to the set of all visited and queued
                Q.append( (infile, nodename) ) # queue up all its children, marking this node as their parent
            nodefile.close()
            #print "Current node: %s" % nodename
            #print "node children", nodedata['inFiles']
            #print "Current Q:", Q
            #print "Current V:", V
            #raw_input("Continue?")
        # make sure we actually have a source node to aim for
        if not source: 
            print "Source node never found. Without it the relevance metric is useless. Skipping..."
            continue
            #quit()
        # we have populated the BFS tree with the path from source to target
        # now traverse up the tree, calculating the relevance score and storing it as we go
        node = source
        source_dist = source.depth
        max_iters = 20
        i = 0
        print "Writing link distances and relevance scores"
        while i <= max_iters and node:
            nodefile = open(data_dir + node.name+'_meta', 'r+')
            nodedata = json.load(nodefile)
            nodedata['distances'].append(node.depth)
            nodedata['relevance'] = relevance(nodedata['distances'], source_dist)
            nodefile.seek(0)
            nodefile.write(json.dumps(nodedata, indent=4))
            nodefile.truncate()
            nodefile.close()
            node = node.parent
            i += 1
        raw_input("Relevance scores calculated for %s, Continue?" % fname)
    print "All Relevance Scores calculated"



""" 
* Helper function to calculate relevance given the source depth and the distances
"""
def relevance(distances, source_depth):
    try:
        dist_avg = sum(distances)/float(len(distances))
        rel = max(1 - dist_avg/source_depth, .1)
        print "Calculated relevance: ", rel
        return rel
    except:
        print "ERROR: Unable to calculate relevance metric"
        return .0001





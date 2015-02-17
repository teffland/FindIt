"""
* Findit utility functions
* This includes feature extractors
"""


"""
* Master function that tests if as url meets the requirements
"""
def is_good_url(url, allowed_domains=None):
    if allowed_domains:                 # check if the url is onsite if we pass sites to filter against
        if is_offsite(allowed_domains, url): 
            #print "Offsite URL: %s" % url
            return False
    if is_cyclic_url(url): return False # check if the url is cyclic (to avoid infitite redirect loops)
    if is_mailto(url): return False     # check if the url is an email address
    if has_no_extension(url): return False # check for a file extension. If there isn't one this probably isn't a page
    if is_image(url): return False      # check for image extension

    # passed all of the tests, so return that it's good
    return True


"""
* Filter offsite domains
* takes allowed domains and list of urls
* checks to see if allowed domain is within the url
"""
def is_offsite(allowed_domains, url):
    if "http" not in url: return False # probably just a local path
    for domain in allowed_domains:
        if domain in url: return False
    return True

"""
# Make Canonical url
* Used to take a url as a string and make into canonical form for crawling
"""
def make_canonical_url(url, current_url=None):
    # change local url to global
    # check for if the url is local or is global
    if "http://" == url[:7] or "https://" == url[:8]: # global url path, so it should be fine
        #print "Global url referred: %s" % url
        return url
    else: # a local url path
        # check for ..'s as these signify how many directories to go back
        urlsplit = url.split('/')
        if urlsplit[0] == '': urlsplit = urlsplit[1:] # if the local started with a / drop it
        #print urlsplit
        backcount = 1 # start with one because we'll always remove the current page
        for s in urlsplit:
            if s == "..": backcount += 1
            else: break
        canon = '/'.join(current_url.split('/')[:-backcount] + urlsplit[backcount-1:]) # now concat the root and the local url with /'s
        #print "Made canonical url %s from %s and %s" % (canon, current_url, url)
    return canon

"""
* Detect cyclic url pattern
* eg, url = a/b/c/d/e/c/d/e (we use this example for comments)
*         is likely a repeating cycle of links that are valid or is a bot trap
*         either way it won't yield any new content
"""
def is_cyclic_url(url_str):
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
def is_mailto(url):
    if 'mailto' in url: return True
    else: return False

"""
* Check for a file name extension. Without one it probably isn't an actual page
*  eg, href="#skip-to-content"
* List of extensions derived from http://www.file-extensions.org/filetype/extension/name/internet-related-files
"""
def has_no_extension(url):
    extensions = ['.aspx', '.html', '.php', '.htm', '.xml', '.pdf', '.asp', '.jspx', '.cshtml', '.phtml', '.xhtml', '.shtml', '.chtml', '.jst', '.html5', '.php4', '.htms', '.rhtml', '.phtm', '.xhtm']
    for ext in extensions:
        if ext in url: return False
    return True

"""
* Test to see if the is an image extension in the url
"""
def is_image(url):
    for ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
        if ext in url.split('.'): return True
    return False

"""
* Take a BeautifulSoup parse tree and remove the style tags and script tags
"""
def remove_scripts_and_style(p):
    for s in p.find_all(['script', 'style']):
        s.decompose()
    return p

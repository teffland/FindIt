"""
* Helper functions to extract all of the features from a webpage
"""
import nltk
import os
import json
import re
import numpy as np
import settings
from numpy import log10
from bs4 import BeautifulSoup
from sklearn.base import TransformerMixin

#global vars
special_chars = ['/', '\\', '=','?','[', ']', ',', '.', ';', ':', '{', '}', '|', '(', ')', '_', '*', '@', '!', '#', '$', '%','^','&', '>', '<', '"']



"""
* Master function featurize a BeautifulSoup parsed page
"""
def featurize_html(content, all_lower=False):
    #content = data['content']
    #print content
    bstree = BeautifulSoup(content)
    tokens = tokenize_body(bstree) # take the body and turn it into a list of tokens
    tokens = strip_specials(tokens) # get rid of special characters in tokens
    tokens = lemmatize(tokens, all_lower=all_lower) # use WordNet to get word stems 
    bigrams = bigramize(tokens)
    tokens += bigrams # add the bigrams of the tokens to the feature vector (doubles the size)
    return tokens # page now represented as list of words and bigrams

def featurize_tokens(tokens, all_lower=False):
    #print tokens
    return lemmatize(strip_specials(tokens), all_lower=all_lower)

def preprocess_html(data, all_lower=False):
    return data['content']

def preprocess_blank(data, all_lower=False):
    return data

"""
* Take page and tokenize it
"""
def tokenize_body(page):
    body = page.find('body')
    if not body: print page
    tokens = body.text.strip().split()
    return tokens

"""
* Strip special chararacters from tokens
* TODO: Make this faster using list comprehensions
"""
def strip_specials(token_list, char_list=special_chars):
    ret = []
    #return [ token for char in char_list for token in token_list if char not in token ] # list comp is faster than two fors
    for token in token_list:
        for char in char_list:
            if char in token:
                token = token.replace(char,"")
        if token != '': ret.append(token)
    return ret

"""
* Lemmatize each of the words, removing morphological affixes
"""
def lemmatize(tokens_list, all_lower=False):
    wnl = nltk.WordNetLemmatizer()
    if all_lower:
        return [ wnl.lemmatize(token.lower()) for token in tokens_list ]
    else:
        return [ wnl.lemmatize(token) for token in tokens_list ]

"""
* Extract bigrams from token tokens_list
* NOTE: We will use the bigrams as a single string joined by a space to allow json output
"""
def bigramize(tokens_list):
    return [' '.join(bigram) for bigram in nltk.bigrams(tokens_list)] # return list instead of generator, saves HUGE time when adding to tokens

"""
* Calculate the Term Frequency (TF) for all terms in a document where 
* tf(term, document) = .5 + .5*freq(term,document)/max_freq(all terms in document)
* source http://en.wikipedia.org/wiki/Tf%E2%80%93idf
"""
def tfs(token_list):
    fq = nltk.FreqDist(token_list) # get the Frequency Distribution 
    mf = float(max(fq.values())) # find the max frequency
    tf = [ (key, .5*((.5*value)/mf)) for key, value in fq.items() ] # return a list of the (term, tf) tuples
    return tf

"""
* Calculate the Inverse Document Frequency for all terms in a document collection index where
* idf(term, document collection) = log(number of documents / (1 + number of documents the word occurs in))
* NOTE: the 1 in the denominator is a correction factor for new terms, it can lead to negative values
* Intuitively this stat measure how common words are in the collection
"""
def idfs(index):
    N = float(len(set([ v for vals in index.values() for v in vals]))) # get total number of docs in index
    idf = [ ( term , log10(N / (1 + len(term_docs)) ) ) for (term, term_docs) in index.items() ] # calculate the idf for each term
    return sorted(idf, key=lambda x:x[1])


"""
* Custom Transformers for sklearn
* Used in the page processing pipeline
"""
"""
* take sparse array and make dense
"""
class DenseTransformer(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        return X.todense()

    def fit(self, X, y=None, **fit_params):
        return self

"""
* Take URL string and parse the url into a list of tokens
* input: list of {content, url, score}
* ouput: list of list of tokens
* split on 'special_chars' += '-'
"""
class UrlParser(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        return [ self.split_url(x['url']) for x in X ]

    def fit(self, X, y=None, **fit_params):
        return self

    def split_url(self, url, split_chars=special_chars):
        return [ token for token in 
                re.split('/|_|-|\.|&|=|%|$|:|;|\'|,|\?', url) if token ]
                # gets rid of the s1 in mathematics11... not good
                #re.split('/|_|-|\.|&|=|%|$|:|;|\'|,|\?|[a-z][0-9]', url) if token ]

"""
* Token counter
* return the number of tokens for each list of tokens
"""
class TermCounter(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        # there has to be a better way to to shape an array  from (600,) to (600,1)
        return np.atleast_2d([ len(x) for x in X ]).T

    def fit(self, X, y=None, **fit_params):
        return self 

"""
* NumberCounter
* return the number of numbers for each token list
"""
class NumberCounter(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        return np.atleast_2d([ len( [ token for token in x if self.isNumber(token)] ) for x in X ]).T

    def fit(self, X, y=None, **fit_params):
        return self 

    def isNumber(self, token):
        try:
            float(token)
            return True
        except:
            return False

"""
* TermJoiner
* Take a list of tokens and return one string joined with ' '
"""
class TermJoiner(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        return [ ' '.join(x) for x in X ]

    def fit(self, X, y=None, **fit_params):
        return self 

"""
*
"""
class UrlAnchorParser(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        return X

    def fit(self, X, y=None, **fit_params):
        return self 

"""
*
"""
class TitleParser(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        return X

    def fit(self, X, y=None, **fit_params):
        return self 

    def split_title(self, url, split_chars=special_chars):
        return [ token for token in 
                re.split('/|_|-|\.|&|=|%|$|:|;|\'|,|\?', url) if token ]
"""
*
"""
class AcronymCounter(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        return X

    def fit(self, X, y=None, **fit_params):
        return self


"""
*
"""
class HtmlParser(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        return [ x['content'] for x in X ] # content from the data dict

    def fit(self, X, y=None, **fit_params):
        return self

"""
* Used to featurize all of the collected data
* DEPRECATED
* TODO: Make featurize over all data folders
"""
def featurize_all():
    # load up the feature index data structure
    index_f = open('../data/feature_index.json', 'r')
    index = json.load(index_f)
    index_f.close()

    # now loop over each content page and featurize it
    # in the first pass we 
    # (1) featurize the document
    # (2) write out the feature vector data as a vocab and TF to the '_data' file 
    # (3) fill in the index as we go to get IDF later
    # in the second pass we use the index to get IDF and multiply by TF to get vector component scores
    data_dir = settings.DATA_DIRECTORY
    files = [ file for file in os.listdir(data_dir) if file[-8:] == "_content" ]
    badset = set()
    #print files
    for counter, fname in enumerate(files):
        f = open(data_dir + fname, 'r') # load the data
        content = json.load(f)
        f.close()
        fshort = fname[:-8] # strip '_content' from name
        try:
            assert 'body' in content['body'] 
            bs = BeautifulSoup(content['body']) # parse it
        except (AssertionError, KeyError):
            print "No body found in content:"
            print content
            print "Skipping this file"
            badset.add(fname) # don't try to read this file later
            continue
        print "\rFeaturizing Page #%i" % counter
        features = featurize(bs) # featurize the parsed html tree
        try:
            assert len(features) > 0
        except AssertionError:
            print "No features collected from %s, body=%s" % (fname, bs)
            print "Skipping this file"
            badset.add(fname) # don't try to read this file later
            continue
        tf = tfs(features)       # calculate term frequency for each feature
        data =  {f[0]:{'tf':f[1], 'idf':None, 'tfidf':None} for f in tf }

        # write out the data we just calculated
        #print "Writing data file %s_data" % fshort
        d = open(data_dir + fshort + '_data', 'w')
        d.write(json.dumps(dict(data), indent=4) + "\n")
        d.close()
        # fill in the index with the features we haven't encountered yet
        for feature in features:
            try:
                if fshort not in set(index[feature]): 
                    index[feature].append(fshort) # index 
            except KeyError:
                index[feature] = [fshort]

    # write back out the completed index
    index_f = open('../data/feature_index.json', 'w')
    index_f.write(json.dumps(dict(index), indent=4) + "\n")
    index_f.close()

    # now the index is complete, so get the IDFs and fill in the TF x IDF score in the data files
    files = [ f for f in files if f not in badset] # remove the ones we never made data files for
    idf = idfs(index)
    for counter, fname in enumerate(files):
        fshort = fname[:-8]
        print "\rWriting TFIDF back for page #%i" % counter
        d = open(data_dir + fshort + '_data', 'r+')
        data = json.load(d)
        for feature, val in idf:
            try:
                tfidf = data[feature]['tf']*val
                data[feature]['idf'] = val
                data[feature]['tfidf'] = tfidf
                #print "Feature %s tfidf: %4f" % (feature, tfidf)
            except KeyError:
                #print 'Feature %s not found in %s' % (feature, fshort)
                continue

        d.seek(0)
        d.write(json.dumps(dict(data), indent=4) + "\n")
        d.truncate()
        d.close()

    # now the data files are populated with the features
    # just read in the relevance score and write out to the data as the label 
    for counter, fname in enumerate(files):
        fshort = fname[:-8]
        d = open(data_dir + fshort + '_meta', 'r')
        meta = json.load(d)
        relevance = meta['relevance']
        print "File %s #%i, relevance = %3f" % (fshort, counter, relevance)
        d.close()
        d = open(data_dir + fshort + '_data', 'r+')
        data = json.load(d)
        data['__relevance__'] = relevance
        d.seek(0)
        d.write(json.dumps(dict(data), indent=4) + "\n")
        d.close()

    print "All data items in %s featurized", data_dir


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
    if not body: 
        #print page
        #print "THIS PAGE HAS NO BODY"
        return [ "THIS", "PAGE", "HAS", "NO" ,"BODY"]
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

    def transform(self, X, **transform_params) :
        return [ self.split_anchor(' '.join(x['text']).strip()) for x in X ]

    def fit(self, X, y=None, **fit_params):
        return self 

    def split_anchor(self, anchor, split_chars=special_chars):
        #print anchor
        if not anchor: return ["No", "anchor"]
        return [ token for token in 
                 re.split('/|_|-|\.|&|=|%|$|:|;|\'|,|\?|\s+|\|', anchor) if token ]

"""
* Title Parser
* take a title string and split on special chars and whitespace
"""
class TitleParser(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        titles = [ x['title'] for x in X ]
        # print titles
        return [ self.split_title(title) for title in titles ]

    def fit(self, X, y=None, **fit_params):
        return self 

    def split_title(self, title, split_chars=special_chars):
        if not title: return ["No", "title"]
        return [ token for token in 
                 re.split('/|_|-|\.|&|=|%|$|:|;|\'|,|\?|\s+|\|', title) if token ]
"""
* AcronymCounter
* Take a list of tokens and return the number of all-uppercase strings in the list 
"""
class AcronymCounter(TransformerMixin):
    def get_params(self, deep=False):
        return {}

    def transform(self, X, **transform_params):
        max_acronym_len = 4
        return np.atleast_2d([ len([token for token in tokens if token.isupper() and len(token) <= max_acronym_len]) for tokens in X ]).T

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

"""
* Test prediction stuff
"""
#from features import featurize_html, featurize_tokens, DenseTransformer, UrlParser, TermCounter, NumberCounter, TermJoiner, UrlAnchorParser, TitleParser, AcronymCounter
from features import *
from settings import DATA_DIRECTORY
from util import make_url_filename
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import LogisticRegression, Lasso, Ridge, ElasticNet
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn import cross_validation as cv
from sklearn.grid_search import GridSearchCV
import json
import numpy as np
from random import shuffle
import pickle

def get_data(data_dirs):
    data_files = []
    for d in data_dirs:
        data_files += [ d+f[:-8] for f in os.listdir(d) if f[-8:] =='_content' ]

    # get data
    print "Getting data"
    docs = []
    targets = []
    urls = []
    url_index = {}
    Xs = []
    #data_files = shuffle(data_files)
    # NEW DATA FORMAT
    for f in data_files:
        p = open(f+'_content', 'r')
        data = json.load(p)
        content = data['html']
        title = data['title'] #['content']
        p.close()
        docs.append(content)
        p = open(f+'_meta', 'r')
        data = json.load(p)
        relevance = data['relevance']
        url = data['url']
        # url object
        url_index[url] = {"url": url,
                          "relevance": data['relevance']
                          }
        # and
        p.close()
        targets.append(relevance)
        urls.append(url)
        X = {'content':content,
             'score':relevance,
             'url':url,
             'title':title}
        Xs.append(X)   
    # for item in url_index.items():
        # print item
    for f in data_files:
        p = open(f+'_meta', 'r')
        data = json.load(p)
        outlinks = data['outLinks']
        p.close() 
        for link in outlinks:
            if link['url'] in url_index.keys():
                try:
                    if not isinstance(link['text'] , basestring): # check if this is a string or a list of strings
                      url_index[link['url']]['text'] += link['text']  
                    else:
                      url_index[link['url']]['text'].append(link['text'])
                except KeyError:
                    url_index[link['url']]['text'] = [ link['text'] ]

    Zs = [ z[1] for z in url_index.items() ]
    for z in Zs:
      try:
        # print z['text']
        z['text']
      except KeyError:
        # print z
        z['text'] = ["No Anchor"]

    return docs, targets, urls, Xs, Zs
"""
    # OLD DATA FORMAT
    for f in data_files:
        p = open(f+'_content', 'r')
        content = json.load(p)['body'] #['content']
        p.close()
        docs.append(content)
        p = open(f+'_meta', 'r')
        data = json.load(p)
        relevance = data['relevance']
        url = data['url']
        p.close()
        targets.append(relevance)
        urls.append(url)
        X = {'content':content,
             'score':relevance,
             'url':url}
        Xs.append(X)    

    return docs, targets, urls, Xs
"""


# load in the data from these folders
data_dirs = [ DATA_DIRECTORY ]
docs, targets, urls, Xs, Zs = get_data(data_dirs) #Xs are page data, Zs are url data
Z_targets = [z['relevance'] for z in Zs]


# extended feature pipeline
page_pipe = Pipeline([
    ('features', FeatureUnion([
        # extract url features
        ('url_features', Pipeline([
            ('url_parser', UrlParser()),
            ('url_sub_features', FeatureUnion([
                #('url_num_terms', TermCounter()), # counts number of tokens
                #('url_num_numbers', NumberCounter()), # counts number of numbers in tokens
                ('url_term_freqs', Pipeline([
                    ('url_term_joiner', TermJoiner()), # change list of tokens into one string for CountVectorizer
                    ('url_term_vec', CountVectorizer(preprocessor=None, 
                                                     tokenizer=featurize_tokens, 
                                                     ngram_range=(1,2),
                                                     max_df=.9
                                                     )),
                    ('url_term_tfidf', TfidfTransformer(use_idf=True))
                    ])) 
                ]))
            ])),
        # extract title features
        ('title_features', Pipeline([
           ('title_parser', TitleParser()),
           ('title_sub_features', FeatureUnion([
               #('title_num_acronyms', AcronymCounter()), # counts number of acronyms in tokens
               #('title_num_numbers', NumberCounter()),   # counts number of numbers in tokens
               ('title_term_freqs', Pipeline([
                   ('title_term_vec', CountVectorizer(preprocessor=preprocess_blank, 
                                                      tokenizer=featurize_tokens, 
                                                      ngram_range=(1,2),
                                                      max_df=.9)),
                   ('title_term_tfidf', TfidfTransformer(use_idf=True))
                   ])) 
               ]))
           ])),
        # extract HTML features
        ('html_features', Pipeline([
            #('html_data_parser', HtmlParser()),
            ('html_term_counts', CountVectorizer(preprocessor=preprocess_html, 
                                                 tokenizer=featurize_html, 
                                                 ngram_range=(1,2),
                                                 max_df=.9
                                                 )),
            ('html_term_tfidf', TfidfTransformer(use_idf=True)),
            ('html_lsa', TruncatedSVD(n_components=500, 
                                      algorithm='randomized',
                                      n_iter=10,
                                      random_state=0))
            ]))

        ])),
    ('dense_features', DenseTransformer()),
    ('reg', RandomForestRegressor(n_estimators=50,
                                  max_features='auto',
                                  n_jobs=2,
                                  verbose=0
                                  ))
    #('reg', Ridge (alpha = .5))
    #('reg', ElasticNet(alpha=.5))
    ])

# """
url_pipe = Pipeline([
    ('features', FeatureUnion([
        # extract url features
        ('url_features', Pipeline([
            ('url_parser', UrlParser()),
            ('url_sub_features', FeatureUnion([
                #('url_num_terms', TermCounter()), # counts number of tokens
                #('url_num_numbers', NumberCounter()), # counts number of numbers in tokens
                ('url_term_freqs', Pipeline([
                    ('url_term_joiner', TermJoiner()), # change list of tokens into one string for CountVectorizer
                    ('url_term_vec', CountVectorizer(preprocessor=None, 
                                                     tokenizer=featurize_tokens, 
                                                     ngram_range=(1,2),
                                                     max_df=.9
                                                     )),
                    ('url_term_tfidf', TfidfTransformer(use_idf=True))
                ]))
            ]))
        ])),           
        # extract url anchor text features
        ('anchor_features', Pipeline([
           ('url_anchor_parser', UrlAnchorParser()),
           ('url_term_joiner', TermJoiner()),
           ('url_anchor_term_vec', CountVectorizer(preprocessor=None, 
                                                   tokenizer=featurize_tokens, 
                                                   ngram_range=(1,2),
                                                   max_df=.9)),
           ('url_term_tfidf', TfidfTransformer(use_idf=True))
           ]))
        ])),
    ('dense_features', DenseTransformer()),
    ('reg', RandomForestRegressor(n_estimators=50,
                                  max_features='auto',
                                  n_jobs=2,
                                  verbose=0
                                  ))
    ]) 
# """

# test out a pipe fixture
"""
pipe_test = Pipeline([
           ('title_parser', TitleParser()),
           ('title_sub_features', FeatureUnion([
               ('title_num_acronyms', AcronymCounter()), # counts number of acronyms in tokens
               ('title_num_numbers', NumberCounter()),   # counts number of numbers in tokens
               ('title_term_freqs', Pipeline([
                   ('title_term_vec', CountVectorizer(preprocessor=preprocess_blank, 
                                                      tokenizer=featurize_tokens, 
                                                      ngram_range=(1,3),
                                                      max_df=.9)), # change these arguments, include bigrams, trigrams
                   ('title_term_tfidf', TfidfTransformer(use_idf=True))
                   ])) 
               ]))
           ])

trans = pipe_test.fit_transform(Xs, targets)
for t in trans:
   print t
"""

# Zs_train, Zs_test, tar_train, tar_test = cv.train_test_split(Zs, Z_targets, test_size=0.5, random_state=0)
# url_pipe.fit(Zs_train, tar_train)
# preds = url_pipe.predict(Zs_test)
# for pred in sorted(zip(preds, Zs_test), key=lambda x:x[0]):
 # print pred
# Grid Search
"""
grid = { 'reg__n_estimators': [10, 20, 30, 40, 50, 100],
                     'reg__max_features': ['auto', 'sqrt', 'log2']
                     }

grid2 = {
        #'features__url_features__url_sub_features__url_term_freqs__url_term_tfidf__use_idf':[False, True],
        'features__url_features__url_sub_features__url_term_freqs__url_term_vec__max_df':[.75, .9, 1.],
        'features__html_features__html_term_counts__ngram_range':[(1,2)],#[(1,1), (1,2), (1,3)],
        'features__html_features__html_term_counts__max_df':[.9],#[.75, .9, 1.],
        'reg__n_estimators':[50,75],#[10,20,30,50,100],
        #'reg__max_features':[None, 'sqrt', 'log2', 'auto'],
        #'reg__max_depth':[None, 2, 5, 10]
        }

Xs_train, Xs_test, tar_train, tar_test = cv.train_test_split(Xs, targets, test_size=0.5, random_state=0)
                    
print "Searching Grid"
gs = GridSearchCV(page_pipe, grid2, cv=5, scoring='mean_absolute_error', n_jobs=-1, verbose=5)
gs.fit(Xs_train, tar_train)

print "Best parameters set found on development set:"
print gs.best_estimator_
for params, mean_score, scores in gs.grid_scores_:
        print "%0.3f (+/-%0.03f) for %r" % (mean_score, scores.std() / 2, params)

pipe_best = gs.best_estimator_
"""

# cross validate
"""
print "Fitting and Scoring w/ Cross Validation new url added pipe"
scores = cv.cross_val_score(page_pipe, Xs[:300], targets[:300], 
                            cv=5, scoring='mean_absolute_error', 
                            n_jobs=1,
                            verbose=2)
print "New CV MSE scores: ", scores
print "MSE: %0.3f (+/- %0.3f)" % (scores.mean(), scores.std())
"""
# look at the individual scores
"""
Xs_train, Xs_test, tar_train, tar_test = cv.train_test_split(Xs[:500], targets[:500], test_size=0.5, random_state=0)
print "Fitting %i training examples" % len(Xs_train)
print "Training Data"
page_pipe.fit(Xs_train, tar_train)
print "Predicting %i test examples"  % len(Xs_test)
predictions = page_pipe.predict(Xs_test)
preds =  zip(predictions, tar_test)
errors = [ ((p - t), t) for (p,t) in preds]
for err in sorted(errors , key=lambda x:x[1]):
    print "%0.4f, %0.3f" % (err[0], err[1])
print ""
"""

"""
i = 0
print "Total Data size: %i" % len(Xs)
for train_i, test_i in cv.KFold(n=len(Xs), n_folds=10, shuffle=True):
    print "Fold #%i" % i
    print "Train i, test i: ", train_i, test_i
    Xs_train, tar_train = Xs[train_i[0]:train_i[-1]], targets[train_i[0]:train_i[-1]]
    Xs_test, tar_test = Xs[test_i[0]:test_i[-1]], targets[test_i[0]:test_i[-1]]
    print "Fitting %i training examples" % len(Xs_train)
    page_pipe.fit(Xs_train, tar_train)
    print "Predicting %i test examples"  % len(Xs_test)
    predictions = page_pipe.predict(Xs_test)
    preds =  zip(predictions, tar_test)
    errors = [ ((p - t), t) for (p,t) in preds]
    for err in sorted(errors , key=lambda x:x[1]):
        print "%0.4f, %0.3f" % (err[0], err[1])
    print ""
    i +=1
"""


# weakly supervised classification of unknowns
"""
print "Weak Supervised:"
X_train, tar_train, url_train = [], [], []
X_test, tar_test, url_test = [], [], []
for x, target, url in zip(Xs, targets, urls):
    if target > 0.001: # if this page was on a relevant path, train on it
        X_train.append(x)
        tar_train.append(target)
        url_train.append(url)
    else: # lets predict on it and see if we can't find more targets
        X_test.append(x)
        tar_test.append(target)
        url_test.append(url)
print "Training Data"
for d in sorted(zip(tar_train, url_train), key=lambda x:x[0]):
    print d

print "Fitting %i labeled data items" % len(X_train)
page_pipe.fit(X_train, tar_train)
print "Predicting %i unlabeled data items" % len(X_test)
pred = page_pipe.predict(X_test)
results = zip(pred, urls)
for i, res in enumerate(sorted(results, key=lambda x:x[0], reverse=True)):
    print i, res


# we need all the target filenames so we can update the inFiles and outFiles of the other data after all of this
"""

"""
new_target_files = []
for i, res in enumerate(sorted(results, key=lambda x:x[0], reverse=True)):
    print i, res
    url = res[1]
    cf = make_url_filename(url, suffix="_content") # content file name
    mf = make_url_filename(url, suffix="_meta") # meta filename

    target = raw_input("Is this a target page? (y/n/m) or (yes/no/maybe):  ").lower()
    if target == "y" or target == "yes":
        print "Ok, giving this page a relevance of 1.0 and labeling as target"
        # get the original content and meta data
        content = json.load( open(cf) ) 
        meta = json.load( open(mf) )
        # change the data to correspond with a target
        content['target'] = True
        meta['target'] = True
        meta['relevance'] = 1.0
        # write out the changed data
        f = open(cf, 'w')
        f.write(json.dumps(content, indent=4) + "\n")
        f.close()
        f = open(mf, 'w')
        f.write(json.dumps(meta, indent=4) + "\n")
        f.close()
        # rename the files as targets
        newcf = make_url_filename(url, prefix = "T_", suffix="_content") # content file name
        newmf = make_url_filename(url, prefix = "T_", suffix="_meta") # meta filename
        os.rename(cf, newcf)
        os.rename(mf, newmf)
        # add this url as a new target file
        new_target_files.append( make_url_filename(url) ) # keep off T_


    elif target == "n" or target == "no":
        print "Ok, giving this page a relevance of .01, if it's on a path it'll be changed when we recompute scores with new targets"
        # get the original content and meta data
        meta = json.load( open(mf) )
        # change the data to correspond with a target
        meta['relevance'] = 0.01
        # write out the changed data
        f = open(mf, 'w')
        f.write(json.dumps(meta, indent=4) + "\n")
        f.close()

    elif target == "m" or target == "maybe":
        print "We'll try this one again later, skipping"

    elif target == "stop":
        print "Tired of labeling? We'll stop for now"
        break
    else:
        print "No valid input given, skipping"

# now that we've gone through every file, we must loop through all of the meta files
# and change the in and out files to reflect the new T_ prefixes
print "Adjusting in and out filenames"
metas = [ fname for fname in os.listdir(DATA_DIRECTORY) if fname[-5:] == "_meta" ]
new_target_set = set(new_target_files)
for fname in metas: # open each meta
    data = json.load(open(DATA_DIRECTORY + fname))
    infiles = []
    # loop over each in path, adding the 'T_' prefix if necessary
    for fpath in data['inFiles']:
        pathsplit = fpath.split('/')
        if (DATA_DIRECTORY + fpath) in new_target_set:
            pathsplit[-1] = 'T_'+pathsplit[-1]
        infiles.append('/'.join(pathsplit))
    data['inFiles'] = infiles
    outfiles = []
    for fpath in data['outFiles']:
        pathsplit = fpath.split('/')
        if fpath in new_target_set:
            pathsplit[-1] = 'T_'+pathsplit[-1]
        outfiles.append('/'.join(pathsplit))  
    data['outFiles'] = outfiles
    # write the fixed data back out
    f = open( DATA_DIRECTORY + fname, 'w')
    f.write(json.dumps(data, indent=4) + "\n")
    f.close()

"""

# train and pickle the estimator piplelines for the test crawler to use
# limit = 500
# page_pipe.fit(Xs[:limit], targets[:limit])
# url_pipe.fit(Zs[:limit], Z_targets[:limit])

print "We have %i total data" % len(Xs)
# only take the "Labeled data"
page_data = [ datum for datum in zip(Xs, targets) if datum[-1] > .001]
Xs = [ datum[0] for datum in page_data]
targets = [ datum[1] for datum in page_data]
url_data = [ datum for datum in zip(Zs, Z_targets) if datum[-1] > .001]
Zs = [ datum[0] for datum in url_data]
Z_targets = [ datum[1] for datum in url_data]

print "We have %i labeled data" % len(Xs)
# only take the "Labeled data"
"""
* Cross Validation of labeled data
"""
print "Page Labeled CV"
page_scores = cv.cross_val_score(page_pipe, Xs, targets, 
                            cv=5, scoring='mean_absolute_error', 
                            n_jobs=2,
                            verbose=1)
print "URL Labeled CV"
url_scores = cv.cross_val_score(url_pipe, Zs, Z_targets, 
                            cv=5, scoring='mean_absolute_error', 
                            n_jobs=2,
                            verbose=1)

print "Page CV MSE scores: ", page_scores
print "MSE: %0.3f (+/- %0.3f)" % (page_scores.mean(), page_scores.std())

print "URL CV MSE scores: ", url_scores
print "MSE: %0.3f (+/- %0.3f)" % (url_scores.mean(), url_scores.std())



# now fit
# """
print "Fitting deployment Regressors on %i labeled page examples and %i labeled url examples" % (len(Xs), len(Zs))
page_pipe.fit(Xs, targets)
url_pipe.fit(Zs, Z_targets)
print "Pickling Regressors"
with open(DATA_DIRECTORY+'../clf/page_pipe.pkl','wb') as f:
  pickle.dump(page_pipe, f)
with open(DATA_DIRECTORY+'../clf/url_pipe.pkl','wb') as f:
  pickle.dump(url_pipe, f)
# """

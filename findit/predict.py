"""
* Test prediction stuff
"""
#from features import featurize_html, featurize_tokens, DenseTransformer, UrlParser, TermCounter, NumberCounter, TermJoiner, UrlAnchorParser, TitleParser, AcronymCounter
from features import *
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn import cross_validation as cv
from sklearn.grid_search import GridSearchCV
import json
import numpy as np
from random import shuffle

def get_data(data_dirs):
    data_files = []
    for d in data_dirs:
        data_files += [ d+f[:-8] for f in os.listdir(d) if f[-8:] =='_content' ]

    # get data
    print "Getting data"
    docs = []
    targets = []
    urls = []
    Xs = []
    #data_files = shuffle(data_files)
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

# load in the data from these folders
data_dirs = ['../data/all/']
docs, targets, urls, Xs = get_data(data_dirs)



# setup processing pipeline
pipe = Pipeline([('term_counts', CountVectorizer(preprocessor=preprocess_blank, 
                                                 tokenizer=featurize_html, 
                                                 ngram_range=(1,3),
                                                 max_df=.9
                                                 )),
                    ('term_tfidf', TfidfTransformer()),
                    ('dense', DenseTransformer()),
                    ('reg', RandomForestRegressor(n_estimators=40, max_features='sqrt'))
#                      ('reg', AdaBoostRegressor()),
#                      ('reg', SVR( kernel='rbf')),
])

# extended feature pipeline
pipe2 = Pipeline([
    ('features', FeatureUnion([
        # extract url features
        ('url_features', Pipeline([
            ('url_parser', UrlParser()),
            ('url_sub_features', FeatureUnion([
                ('url_num_terms', TermCounter()), # counts number of tokens
                ('url_num_numbers', NumberCounter()), # counts number of numbers in tokens
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
        # extract url anchor text features
        # NOTE: THERE IS NO ANCHOR TEXT FOR THE CURRENT PAGE URL
        #('anchor_features', Pipeline([
        #    ('url_anchor_parser', UrlAnchorParser()),
        #    ('url_anchor_term_vec', CounterVectorizer()) #change these arguments, include bi and trigrams
        #    # possibly include tf(idf)
        #    ])),
        
        # extract title features
        #('title_features', Pipeline([
        #    ('title_parser', TitleParser()),
        #    ('title_sub_features', FeatureUnion([
        #        ('title_num_acronyms', AcronymCounter()), # counts number of acronyms in tokens
        #        ('title_num_numbers', NumberCounter()),   # counts number of numbers in tokens
        #        ('title_term_freqs', Pipeline([
        #            ('title_term_vec', CountVectorizer()), # change these arguments, include bigrams, trigrams
        #            ('title_term_tfidf', TfidfTransformer())#idf=False))
        #            ])) 
        #        ]))
        #    ])),
        # extract HTML features
        # TODO: Add known term list cross-referencing as second feature
        ('html_features', Pipeline([
            #('html_data_parser', HtmlParser()),
            ('html_term_counts', CountVectorizer(preprocessor=preprocess_html, 
                                                 tokenizer=featurize_html, 
                                                 ngram_range=(1,2),
                                                 max_df=.9
                                                 )),
            ('html_term_tfidf', TfidfTransformer())
            ]))

        ])),
    ('dense_features', DenseTransformer()),
    ('reg', RandomForestRegressor(n_estimators=50,
                                  max_features='auto'
                                  ))
    ])

"""
pipe_test = Pipeline([
            ('title_parser', TitleParser()),
            ('title_sub_features', FeatureUnion([
                ('title_num_acronyms', AcronymCounter()), # counts number of acronyms in tokens
                ('title_num_numbers', NumberCounter()),   # counts number of numbers in tokens
                ('title_term_freqs', Pipeline([
                    ('title_term_vec', CountVectorizer()), # change these arguments, include bigrams, trigrams
                    ('title_term_tfidf', TfidfTransformer())#idf=False))
                    ])) 
                ]))
            ])

"""
#trans = pipe2.fit_transform(Xs, targets)
#for t in trans:
#    print t

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
gs = GridSearchCV(pipe2, grid2, cv=5, scoring='mean_absolute_error', n_jobs=-1, verbose=5)
gs.fit(Xs_train, tar_train)

print "Best parameters set found on development set:"
print gs.best_estimator_
for params, mean_score, scores in gs.grid_scores_:
        print "%0.3f (+/-%0.03f) for %r" % (mean_score, scores.std() / 2, params)

pipe_best = gs.best_estimator_
"""

# cross validate
"""
print "Fitting and Scoring w/ Cross Validation Original pipe"
scores = cv.cross_val_score(pipe, docs, targets, 
                            cv=6, scoring='mean_absolute_error', 
                            n_jobs=2)
print "OG CV MSE scores: ", scores
print "MSE: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2)
"""

print "Fitting and Scoring w/ Cross Validation new url added pipe"
scores = cv.cross_val_score(pipe2, Xs, targets, 
                            cv=6, scoring='mean_absolute_error', 
                            n_jobs=-1)
print "New CV MSE scores: ", scores
print "MSE: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std())

# look at the individual scores
"""
for train_i, test_i in cv.KFold(n=len(docs), n_folds=10, shuffle=True):
    #print "Train i, test i: ", train_i, test_i
    doc_train, tar_train = docs[train_i[0]:train_i[-1]], targets[train_i[0]:train_i[-1]]
    doc_test, tar_test = docs[test_i[0]:test_i[-1]], targets[test_i[0]:test_i[-1]]
    pipe.fit(doc_train, tar_train)
    predictions = pipe.predict(doc_test)
    preds =  zip(predictions, tar_test)
    errors = [ ((p - t), t) for (p,t) in preds]
    for err in sorted(errors , key=lambda x:x[1]):
        print "%0.4f, %0.3f" % (err[0], err[1])
    print ""
"""
"""
# weakly supervised classification of unknowns
print "Weak Supervised:"
X_train, tar_train, url_train = [], [], []
X_test, tar_test, url_test = [], [], []
for x, target, url in zip(Xs, targets, urls):
    if target >= 0.01: # if this page was on a relevant path, train on it
        X_train.append(x)
        tar_train.append(target)
        url_train.append(url)
    else: # lets predict on it and see if we can't find more targets
        X_test.append(x)
        tar_test.append(target)
        url_test.append(url)


print "Fitting"
pipe2.fit(X_train, tar_train)
print "Predicting"
pred = pipe2.predict(X_test)
results = zip(pred, urls)
for res in sorted(results, key=lambda x:x[0]):
    print res
"""


# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 13:22:01 2017

@author: Ryan McMahon
"""

import argparse
import os
import re
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.mixture import BayesianGaussianMixture

def tokenizer(x):
    return re.split('\s+', x)

cv = CountVectorizer(tokenizer=tokenizer, max_df=0.9, min_df=0.05)

dpgmm = BayesianGaussianMixture(
    n_components=100, covariance_type='full', 
    weight_concentration_prior=100, mean_precision_prior=0.5,
    weight_concentration_prior_type='dirichlet_process',
    n_init=1, init_params="random", max_iter=100, random_state=2)

df = pd.read_csv('D:/cong_text/csvs/tokenized/topicmodeling/ExpAgendas/topictext_114Cong.csv', encoding='utf-8')
df = df.dropna()


# Split into training and test sets:
np.random.seed(1)
n_train = int(len(df.index) * 0.75)
df_idx = np.array(df.index)
np.random.shuffle(df_idx)
train_samp = df_idx[:n_train]

train = list(df.topic_text.loc[df.index.isin(train_samp)])
test = list(df.topic_text.loc[~df.index.isin(train_samp)])

X = cv.fit_transform(train)

X = X.todense()

dpgmm.fit(X)

w = dpgmm.weights_
plt.bar([i for i in range(1,101)], w)

len(np.argwhere(w >= 0.01))
# 32 components w/ weights greater than 0.01 (i.e., 1% of docs) -> similar to ExpAgenda model
len(np.argwhere(w >= 0.009))
# 42 components w/ weights greater than 0.009 (i.e., 0.9% of docs)



### Examine word covariances and topics:
words = cv.get_feature_names()

## look at largest component:
bigtopic = dpgmm.means_[99,:]
bigtopwords = [words[i] for i in np.argsort(bigtopic)[-15:]]
# Education and funding mixture, which makes sense given topic distributions from ExpAgenda

## look at expected word covariances:
# presidential topic (topic 30 in final ExpAgenda, 4.29% of docs, 6th ''largest'' topic)
words.index('obama'), words.index('presid')
# (456, 506)

# get estimated covariance of these words
pres_cov = dpgmm.covariances_[:,456,506]

# what component is this covariance largest in?
np.argwhere(pres_cov == pres_cov.max())
# array([[98]], dtype=int64); which is the 2nd largest component weight in model

       
## look at 3rd largest topic:
topic3 = dpgmm.means_[97,:]
topic3words = [words[i] for i in np.argsort(topic3)[-15:]]
# pork spending, funding, symbolic mixture - again makes sense w/ ExpAgenda fit.
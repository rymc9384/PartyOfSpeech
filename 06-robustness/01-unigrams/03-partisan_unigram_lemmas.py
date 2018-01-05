# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 13:09:36 2017

@author: Ryan McMahon
"""

import pickle
import re
import pandas as pd

from utils import fightinwords


#########################
### 0) LEMMAS
#########################

# 0.0a) Read in lemma DTM build
with open("D:/cong_text/robust/DTMs/unilem_dtmbuildobj.pkl", "rb") as f:
    dtmbuild = pickle.load(f)

# 0.0b) Extract features
FEATS = dtmbuild.DTM_features

# 0.0c) Remove DTM build (save memory)
del dtmbuild


# 0.1) Find different word classes in feature set
NNPs = [x for x in FEATS if re.search('\_NNP', x) is not None]
NNs = [x for x in FEATS if re.search('\_(NNS?$|PRP)', x) is not None] # includes pronouns
PRPs = [x for x in FEATS if re.search('\_PRP', x) is not None]
JJs = [x for x in FEATS if re.search('\_JJ$', x) is not None]


#########################
### 1) COUNTS
#########################

# 1.0) Read in word counts
counts = pd.read_csv("D:/cong_text/robust/DTMs/unilem_partytopiccounts.csv", encoding='utf-8')

# 1.1) Add in word column
counts['word'] = FEATS

# 1.2a) Index columns w/ priors
PCOLS = [i for i in range(2, 182,4)] + [i for i in range(3, 183, 4)]
PCOLS.sort()
PCOLS = [counts.columns[i] for i in PCOLS]

# 1.2b) Add 0.01 to prior columns w/ a minimum of 0:
for i in PCOLS:
    if counts[i].min() == 0:
        counts[i] += 0.01
              
              
#########################
### 2) MOST PARTISAN (uninformative Dirichlet)
#########################

# 2.0) Fit model on all topics
fw0 = fightinwords(words=counts.word,
                   counts1=counts.gopcounts0,
                   counts2=counts.demcounts0,
                   priors1=counts.goppriors0, 
                   priors2=counts.dempriors0)


# 2.1) Pronouns
fw0_prp = fw0.loc[fw0.word.isin(PRPs),:]
fw0_prp = fw0_prp.sort_values(by='zeta', ascending=False)

# 2.2) Nouns (excluding proper nouns + pronouns)
fw0_nns = fw0.loc[fw0.word.isin(NNs),:]
fw0_nns = fw0_nns.sort_values(by='zeta', ascending=False)


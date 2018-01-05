# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 11:51:24 2017

@author: Ryan McMahon
"""

import argparse
import pickle
import re
import pandas as pd

from utils import fightinwords



with open("D:/cong_text/robust/DTMs/unilem_dtmbuildobj.pkl", "rb") as f:
    dtmbuild = pickle.load(f)

FEATS = dtmbuild.DTM_features

del dtmbuild

NNPs = [x for x in FEATS if re.search('\_NNP', x) is not None]
NNs = [x for x in FEATS if re.search('\_NNS?$', x) is not None]
PRPs = [x for x in FEATS if re.search('\_PRP', x) is not None]
JJs = [x for x in FEATS if re.search('\_JJ$', x) is not None]

counts = pd.read_csv("D:/cong_text/robust/DTMs/unilem_partytopiccounts.csv", encoding='utf-8')

counts['word'] = FEATS

# prior columns (to add 0.01)
PCOLS = [i for i in range(2, 182,4)] + [i for i in range(3, 183, 4)]
PCOLS.sort()
PCOLS = [counts.columns[i] for i in PCOLS]

for i in PCOLS:
    if counts[i].min() == 0:
        counts[i] += 0.01

fw1 = fightinwords(words=counts.word,
                   counts1=counts.gopcounts0,
                   counts2=counts.demcounts0,
                   priors1=counts.goppriors0, 
                   priors2=counts.dempriors0)

fw1_0 = fw1.loc[~fw1.word.isin(NNPs),:]
fw1_prp = fw1.loc[fw1.word.isin(PRPs),:]
fw1_nns = fw1.loc[fw1.word.isin(NNs),:]


fw35 = fightinwords(words=counts.word,
                   counts1=counts.gopcounts35,
                   counts2=counts.demcounts35,
                   priors1=counts.goppriors35, 
                   priors2=counts.dempriors35)

fw35_0 = fw1.loc[~fw35.word.isin(NNPs),:]

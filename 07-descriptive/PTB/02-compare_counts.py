# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 11:50:45 2018

@author: Ryan McMahon
"""

import numpy as np
from utils import featureset, logodds, getc

# load PTB features and DTM
ptb = featureset(featurefile="D:/cong_text/final_pos/ptb/ptb_dtm_vocab.pkl")
ptb.loadself()

# load Sen features and DTM
sen = featureset(featurefile="D:/cong_text/final_pos/DTMs/newfeatures_vocab.pkl", \
                 countsfile="D:/cong_text/final_pos/DTMs/party_counts_topic0.pkl")
sen.loadself()
sen.loadcounts()


# feature counts for ptb + sen
ptb.builddf(sen=False, features=ptb.prpnum_feats)
sen.builddf(sen=True, features=sen._prpnum_feats)


ptb_c, ptb_t = getc(ptb.temp_df, 'PRPPLUR')
sen_c, sen_t = getc(sen.temp_df, 'PRPPLUR')
d,se = logodds(ptb_c, ptb_t, sen_c, sen_t)
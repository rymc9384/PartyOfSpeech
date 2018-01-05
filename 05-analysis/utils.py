# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 09:16:58 2017

@author: Ryan McMahon
"""

import pickle
import re
import numpy as np
import pandas as pd

from glob import glob


class featureset(object):
    
    def __init__(self, featurefile="D:/cong_text/final_pos/DTMs/newfeatures_vocab.pkl"):
        self._featurefile = featurefile
        
    def loadself(self):
        with open(self._featurefile, "rb") as f:
            tmp_dict = pickle.load(f)
            
        self.__dict__.update(tmp_dict)
        
    

class datautils(object):
    
    def __init__(self, features=None, countspathpattern="D:/cong_text/final_pos/DTMs/party_counts*"):
        
        self._features = features
        self._countspathpattern = countspathpattern
        
        self._countsfiles = glob(countspathpattern)
        self._topicidx = [int(re.sub("[^\d+]", '', f)) for f in self._countsfiles]
        
        self._tempcountsfile = None
        self._tempcounts = None
        self._tempdf = None
        
        
    def load_counts(self, topic=0):
        self._temptopic = topic
        self._tempcountsfile = self._countsfiles[self._topicidx.index(topic)]
        
        with open(self._tempcountsfile, "rb") as f:
            self._tempcounts = pickle.load(f)
    

    def builddf(self):
        feats = pd.Series(self._features, name="words")
        feats = feats.to_frame()
        feats['gopcounts'] = self._tempcounts[0]
        feats['demcounts'] = self._tempcounts[1]
        feats['goppriors'] = self._tempcounts[2]
        feats['dempriors'] = self._tempcounts[3]
        feats = feats.groupby('words', as_index=False).sum()
        feats = feats[(feats.gopcounts > 0) | (feats.demcounts > 0)]
        
        
        if feats.goppriors.min() == 0 or feats.dempriors.min() == 0:
            feats.goppriors += 0.01
            feats.dempriors += 0.01
            
        self._tempdf = feats
        
    
class analysisutils(object):
    
    def __init__(self, wordcounts=None):
        
        self._wordcounts = wordcounts
        self._fwoutput = None
        
    
    def fightinwords(self):
        ###########################################################################
        # - NOTE: Adapted from "bayes_compare_language" function by Jack Hessel, 
        #           Dept. of Comp Sci, Cornell University. 
        #    
        # - PURPOSE: This is a function to estimate the zetas of 
        #               Fightin' Words (Monroe et al. 2008), which are related to 
        #               the differential use of words by two or more groups.
        #
        # - ARGUMENT(S): 1) 'words' = a vector of words associated with the counts;
        #                2) 'counts1' = a vector of word counts by group 1;
        #                3) 'counts2' = a vector of word counts by group 2;
        #                4) 'gopprior' = a vector of values, which essentially add 
        #                               prior_w observations of word 'w' to the
        #                               total observed count of word 'w' by 
        #                               group 1.
        #                5) 'demprior' = same as (4) but for group 2.
        #                
        #
        # - OUTPUT: A pandas dataframe w/ words, zeta values, and total counts
        #
        ###########################################################################
        
        words = self._wordcounts.words
        counts1 = self._wordcounts.gopcounts
        counts2 = self._wordcounts.demcounts
        priors1 = self._wordcounts.goppriors
        priors2 = self._wordcounts.dempriors
        
        # Make sure everything is a list:
        if type(words) != list:
            words = list(words)
        if type(counts1) != list:
            counts1 = list(counts1)
        if type(counts2) != list:
            counts2 = list(counts2)
        if type(priors1) != list:
            priors1 = list(priors1)
        if type(priors2) != list:
            priors2 = list(priors2)
        
        # Sum of priors (alpha_0) by party
        a01 = np.sum(priors1)
        a02 = np.sum(priors2)
        n1 = np.sum(counts1) 
        n2 = np.sum(counts2)
        
        # compute delta
        term1 = np.log( np.add(counts1, priors1) /(n1 + a01 - np.add(counts1, priors1)))
        term2 = np.log( np.add(counts2, priors2) /(n2 + a02 - np.add(counts2, priors2)))
        
        delta = np.subtract(term1,term2)
            
        # compute variance on delta
        var = np.add( 1 / np.add(counts1, priors1), 1 / np.add(counts2, priors2) )
        
        # list of zetas (positive zetas indicate the word is associated w/ group1)
        z_scores = list(np.divide(delta, np.sqrt(var)))
            
        # store total count:
        full_counts = list(np.add(counts1, counts2))
            
        # Put into data frame:
        rows = [[row[0], row[1], row[2]] for row in zip(words,z_scores,full_counts)]
        out = pd.DataFrame(rows)
        out.columns = ['word','zeta','count']
        
        self._fwoutput = out
        
        
    def get_top_features(self, n=15):
        """
        Get output for `n` features most strongly associated with each group
        """
        
        tmp_df = self._fwoutput.sort_values('zeta', ascending=False)
        
        self._topn_gop = tmp_df.head(n=n)
        self._topn_dem = tmp_df.tail(n=n)
        print("Top {} Republican Features:".format(n))
        print(self._topn_gop)
        print("\nTop {} Democratic Features:".format(n))
        print(self._topn_dem)
    
    
    def get_word(self, word):
        
        return self._fwoutput[self._fwoutput.word == word]
        
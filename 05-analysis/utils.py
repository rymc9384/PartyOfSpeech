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
        tmp_files = [re.sub(r".*?\\", "", f) for f in self._countsfiles]
        self._topicidx = [int(re.sub("[^\d+]", '', f[3:])) for f in tmp_files]
        
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
        
        deltas = np.subtract(term1,term2)
            
        # compute variance on delta
        var = np.add( 1 / np.add(counts1, priors1), 1 / np.add(counts2, priors2) )
        
        # list of zetas (positive zetas indicate the word is associated w/ group1)
        z_scores = list(np.divide(deltas, np.sqrt(var)))
            
        # store total count:
        full_counts = list(np.add(counts1, counts2))
            
        # Put into data frame:
        rows = [[row[0], row[1], row[2], row[3]] for row in zip(words,z_scores,deltas,full_counts)]
        out = pd.DataFrame(rows)
        out.columns = ['word','zeta','delta','count']
        
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
        

def tokenizer(x):
    return x.split(' ')  		
		
class buildrawdtm(object):
    
    def __init__(self, ub_min=0.9, lb_max=0.005, ngrams=(1,3), lower=False, \
                 tokenizer=tokenizer):
        self.__ub_min = ub_min
        self.__lb_max = lb_max
        self.__ngrams = ngrams
        self.__lower = lower
        
        self.__tokenizer = tokenizer
        
        self.__CVub = CountVectorizer(min_df=ub_min, tokenizer=self.__tokenizer, \
                                      ngram_range=ngrams, lowercase=lower)
        self.__CVlb = CountVectorizer(max_df=lb_max, tokenizer=self.__tokenizer, \
                                      ngram_range=ngrams, lowercase=lower)
        self.__CVfull = CountVectorizer(tokenizer=self.__tokenizer, \
                                        ngram_range=ngrams, lowercase=lower)
        
        self.commonngrams_general = []
        self.commonngrams_sens = []
        
      
    def fit_transformfull(self, text):
        """
        Fit a countvectorizer to the text.
        """
        
        self.DTM = self.__CVfull.fit_transform(text)
        self.DTM_features = self.__CVfull.get_feature_names()
        self.nrows, self.ncols = self.DTM.shape
        
        
    def get_commonngrams(self, text, general=False):
        """
        Get ngrams that appear in 90% or more of texts.
        """
        
        CVcommon = self.__CVub.fit(text)
        
        if general:
            self.commonngrams_general += CVcommon.get_feature_names()
        else:
            self.commonngrams_sens += CVcommon.get_feature_names()
            self.commonngrams_sens = list(set(self.commonngrams_sens))
            
    
    def get_rarengrams(self, text):
        """
        Get ngrams that appear in 0.5% or less of texts.
        """
        
        CVrare = self.__CVlb.fit(text)
        self.rarengrams = CVrare.get_feature_names()
        
    
    def make_exclusive_commonngrams(self):
        """
        Take the senator specific and general commonngrams and make them 
        mutually exclusive lists.
        """
    
        self.commonngrams_sens = [x for x in self.commonngrams_sens if x not in self.commonngrams_general]
    

    def get_tagsonly(self):
        """
        Generate tag only feature names
        """
        
        self.tagonly_features = [re.sub('[^\s]+_', '', feat) for feat in self.DTM_features]
         
        
    def make_replacement_feats(self, which='general'):
        """
        Make the replacements for the common or rare features (e.g., the_DT -> GENERAL_DT)
        ############
        ## ARGS: 
        #  1) which (str) = name of ngram list to operate on; 
        #                   which \in ['general', 'sens', 'rare']
        #
        ############
        """
        
        which = which.lower()
        if which not in ['general', 'sens', 'rare']:
            print("which arg not in ['general', 'sens', 'rare']!")
            raise(TypeError)
        
        if which == 'general':
            self.general_replacements = [re.sub('\\w+(?=_)', 'GENERAL', x) for x in self.commonngrams_general]
        elif which == 'sens':
            self.sens_replacements = [re.sub('\\w+(?=_)', 'SPECIFIC', x) for x in self.commonngrams_sens]
        else:
            self.rare_replacements = [re.sub('\\w+(?=_)', 'RARE', x) for x in self.rarengrams]
            
            
        
    def substitutefeats(self, toreplace, replacement, tagsonly=False):
        """
        Edit feature names for rare or common features.
        
        ############
        ## ARGS: 
        #  1) toreplace (list) = list of featurenames to edit
        #  2) replacement (list) = list of replacements for those edits;
        #                           need to be ordered 1:1 with the toreplace list
        #  3) tagsonly (bool) = editing tagonly feature names or not; default = False
        #
        #############
        """
        
        if not tagsonly:
            for i in range(len(toreplace)):
                tempidx = self.DTM_features.index(toreplace[i])
                self.DTM_features[tempidx] = replacement[i]
        else:
            for i in range(len(toreplace)):
                tempidx = self.tagonly_features.index(toreplace[i])
                self.tagonly_features[tempidx] = replacement[i]
        

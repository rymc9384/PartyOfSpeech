# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 10:42:20 2018

@author: Ryan McMahon
"""

import nltk
import numpy as np
import pandas as pd
import pickle
import re

from sklearn.feature_extraction.text import CountVectorizer



def tokenizer(text):
    return text.split(' ')


class cleanptb(object):
    
    def __init__(self, ngrams=(1,3), tokenizer=tokenizer, indata=None):
        
        if indata is None:
            indata = list(nltk.corpus.treebank.tagged_sents())
            
        self.ngrams = ngrams
        self.tokenizer = tokenizer
        self.indata = indata
        self.vectorizer = CountVectorizer(tokenizer=tokenizer, \
                                          ngram_range=ngrams, \
                                          lowercase=False)
        
        
        # to create
        self.sents = None
        self.DTM = None
        self.raw_feats = None
        self.raw_tags = None
        self.raw_prpnum_feats = None # token + tag
        self.prpnum_feats = None # tags only
        self.vrbtense_feats = None
        self.nounnum_feats = None
        self.allnouns_feats = None
        self.nopropnouns_feats = None
        
        # regex commands
        self._prpsing_re = re.compile("((?<=i)|(?<=(me|he|it|my))|" +
                        "(?<=(she|him|her|his|its))|" +
                        "(?<=(this|that|mine|hers))|" +
                        "(?<=myself)|(?<=(himself|herself))|(?<=yourself))" +
							"_PRP\$?")
        self._prpplur_re = re.compile("((?<=(we|us))|(?<=our)|" +
                        "(?<=(they|them|ours))|" +
                        "(?<=(these|those|their))|(?<=theirs)|" +
                        "(?<=ourselves)|" +
                        "(?<=(yourselves|themselves)))_PRP\$?")

        self._past_re = re.compile("(VBD|VBN)")
        self._future_re = re.compile("(MD VB|MD RB VB)(?=\s|$)")
        self._nnsing_re = re.compile("(PRPSING|NN|NNP)(?=\s|$)")
        self._nnplur_re = re.compile("(PRPPLUR|NNS|NNPS)(?=\s|$)")
        self._gettags_re = re.compile("[^\s]+_")
        self._nopropnouns_re = re.compile("(PRPSING|PRPPLUR|NN|NNS)(?=\s|$)")
        self._propnouns_re = re.compile("(NNP|NNPS)(?=\s|$)")


    def format_nltk_data(self):
        """
        Makes list of sentences, with elements are 'WORD TAG' pairs 
        Args:
            data: list of sentences with (WORD, TAG) tuple elements
        Returns:
            List of sentences, with elements are 'WORD_TAG' pairs 
            
        Example:
        data = [[('The', 'DET'), ('cat', 'NN')], [(WORD, TAG), ...]]
        returns: [['the_DET', 'cat_NN'], [WORD_TAG,...]]
        """
        
        sents = []
        
        for d in self.indata:
            t_d = [x.lower() + '_' + y for x,y in d]
            sents.append(t_d)
        
        self.sents = [' '.join(s) for s in sents]
        
    def fit_dtm(self):
        
        self.DTM = self.vectorizer.fit_transform(self.sents)
        self.raw_feats = self.vectorizer.get_feature_names()
    

    def makefeats(self):
        # pronoun number
        self.raw_prpnum_feats = [re.sub(self._prpsing_re, '_PRPSING', feat) for feat in self.raw_feats]
        self.raw_prpnum_feats = [re.sub(self._prpplur_re, '_PRPPLUR', feat) for feat in self.raw_prpnum_feats]
        
        # tags w/ and w/o new pronoun tags
        self.raw_tags = [re.sub(self._gettags_re, '', feat) for feat in self.raw_feats]
        self.prpnum_feats = [re.sub(self._gettags_re, '', feat) for feat in self.raw_prpnum_feats]
        
        # verb tense
        self.vrbtense_feats = [re.sub(self._past_re, 'VBPAST', feat) for feat in self.raw_tags]
        self.vrbtense_feats = [re.sub(self._future_re, 'VBFUT', feat) for feat in self.vrbtense_feats]
       
        # noun number
        self.nounnum_feats = [re.sub(self._nnsing_re, 'NNSING', feat) for feat in self.prpnum_feats]
        self.nounnum_feats = [re.sub(self._nnplur_re, 'NNPLUR', feat) for feat in self.nounnum_feats]
        
        # larger noun tags w/ and w/o proper nouns
        self.nopropnouns_feats = [re.sub(self._nopropnouns_re, 'NOUN', feat) for feat in self.prpnum_feats]
        self.allnouns_feats = [re.sub(self._propnouns_re, 'NOUN', feat) for feat in self.nopropnouns_feats]
        
    
    def save(self, outfile="D:/cong_text/final_pos/ptb/ptb_dtm_vocab.pkl"):
        
        with open(outfile, "wb") as f:
            pickle.dump(self.__dict__, f, protocol=-1)




# Be able to load the dtms/features
class featureset(object):
    
    def __init__(self, featurefile="D:/cong_text/final_pos/ptb/ptb_dtm_vocab.pkl", countsfile=None):
        self._featurefile = featurefile
        self._countsfile = countsfile
        
    def loadself(self):
        with open(self._featurefile, "rb") as f:
            tmp_dict = pickle.load(f)
            
        self.__dict__.update(tmp_dict)
        
    def loadcounts(self):
        with open(self._countsfile, "rb") as f:
            self._tempcounts = pickle.load(f)
            
    def builddf(self, sen=False, features=None):
        feats = pd.Series(features, name="words")
        feats = feats.to_frame()
        
        # if sen, combine the gop and dem counts:
        if sen:
            feats['counts'] = np.add(self._tempcounts[0], self._tempcounts[1])
        else:
            feats['counts'] = self.DTM.sum(axis=0).tolist()[0]
            
        feats = feats.groupby('words', as_index=False).sum()
        self.temp_df = feats


def logodds(ptb_c, ptb_t, sen_c, sen_t):
    
    # Treat ptb as x = 1, sen as x = 0
    # feat count as y = 1, total - count as y = 0
    # thus n11 = ptb_c and n10 = ptb_t - ptb_c
    # lodds > 0 indicate word is associated w/ PTB corpus
    
    n11 = ptb_c
    n10 = ptb_t - ptb_c
    n01 = sen_c
    n00 = sen_t - sen_c
    
    odds = (n11 * n00) / (n10 * n01)
    lodds = np.log(odds)
    
    se = np.sqrt(1/n11 + 1/n00 + 1/n01 + 1/n00)
    
    return(lodds, se)

def getc(df, feat):
    
    c = df.counts[df.words == feat].values[0]
    t = df.counts.sum()
    
    return(c,t)



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
        #                4) 'priors1' = a vector of values, which essentially add 
        #                               prior_w observations of word 'w' to the
        #                               total observed count of word 'w' by 
        #                               group 1.
        #                5) 'priors2' = same as (4) but for group 2.
        #                
        #
        # - OUTPUT: A pandas dataframe w/ words, zeta values, and total counts
        #
        ###########################################################################
        
        words = self._wordcounts.words
        counts1 = self._wordcounts.counts1
        counts2 = self._wordcounts.counts2
        priors1 = self._wordcounts.priors1
        priors2 = self._wordcounts.priors2
        
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
        rows = [[row[0], row[1], row[2], row[3]] for row in zip(words,z_scores,delta,full_counts)]
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
        print("Top {} Group 1 Features:".format(n))
        print(self._topn_gop)
        print("\nTop {} Group 2 Features:".format(n))
        print(self._topn_dem)
    
    
    def get_word(self, word):
        
        return self._fwoutput[self._fwoutput.word == word]
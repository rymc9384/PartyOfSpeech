# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 15:13:58 2017

@author: Ryan McMahon
"""

import re
import pickle
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer


def tokenizer(x):
    return x.split(' ')


def fightinwords(words, counts1, counts2, priors1, priors2):
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
    #                4) 'prior1' = a vector of values, which essentially add
    #                               prior_w observations of word 'w' to the
    #                               total observed count of word 'w' by
    #                               group 1.
    #                5) 'prior2' = same as (4) but for group 2.
    #
    #
    # - OUTPUT: A pandas dataframe w/ words, zeta values, and total counts
    #
    ###########################################################################



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

    return out


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




class topiccounts(object):

    def __init__(self, counts = {}, avgdoclen = None, ndocs = None, \
                 GOPidx = None, DEMidx = None):
        self.counts = counts
        self.__avgdoclen = avgdoclen
        self.__ndocs = ndocs
        self.__GOPidx = GOPidx
        self.__DEMidx = DEMidx


    def counttopic(self, DTM, Tidx, topic):
        """
        featurecounts for parties by topic
        DTM (scipy.sparse.csr.csr_matrix) = DocTermMatrix
        Tidx (list(bool)) = True where docs are from topic
        topic (int) = The topic number

        equation citations from Monroe et al. (2008)
        """



        if topic == 0:
            Rtopic, Dtopic = np.array(self.__GOPidx), np.array(self.__DEMidx)
            Rtopic = list(np.where(Rtopic == True)[0])
            Dtopic = list(np.where(Dtopic == True)[0])

            self.counts[topic] = [DTM[Rtopic,:].sum(axis=0).tolist()[0], \
                        DTM[Dtopic,:].sum(axis=0).tolist()[0], \
                        [0.01]*DTM.shape[1], [0.01]*DTM.shape[1]]

        else:
            Rtopic = [bool(self.__GOPidx[i] * Tidx[i]) for i in range(self.__ndocs)]
            Dtopic = [bool(self.__DEMidx[i] * Tidx[i]) for i in range(self.__ndocs)]

            Rtopic, Dtopic = np.array(Rtopic), np.array(Dtopic)
            Rtopic = list(np.where(Rtopic == True)[0])
            Dtopic = list(np.where(Dtopic == True)[0])

            othertopics = np.array(Tidx)
            othertopics = list(np.where(othertopics == False)[0])

            prior_counts = DTM[othertopics,:].sum(axis=0) # word counts in prior samp (i.e., 'y' in eq. 23)
            prior_sum = prior_counts.sum() # sum of prior word counts (i.e., 'n' in eq. 23)

            Rdocscale, Ddocscale = len(Rtopic), len(Dtopic) # scale prior by number of docs in topic authored by each party
            alpha0R= self.__avgdoclen * Rdocscale # imply alpha 0 words per document of Republicans (i.e., 'a0' in eq. 23)
            alpha0D = self.__avgdoclen * Ddocscale

            prior_vectorR = prior_counts * ( alpha0R / prior_sum ) # informative prior for gop
            prior_vectorD = prior_counts * ( alpha0D / prior_sum )

            prior_vectorR = prior_vectorR.tolist()[0] # put into list
            prior_vectorD = prior_vectorD.tolist()[0]

            self.counts[topic] = [DTM[Rtopic,:].sum(axis=0).tolist()[0], \
                        DTM[Dtopic,:].sum(axis=0).tolist()[0], \
                        prior_vectorR, prior_vectorD]

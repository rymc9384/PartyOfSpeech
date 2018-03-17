# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 10:47:20 2017

@author: Ryan McMahon
"""

import re
import pickle
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer


class lemtag:
    
    class Config:
        tagbasepath = "D:/cong_text/csvs/tagged/"
        tagrawpath = "./fixedparenths/"
        taglemmapath = "./lemmatized/"
        lemmafinalout = "lemma_merged_id.csv"
    
    
    def loadrawlem(rawf, lemf):
        """
        Load raw and lemmatized tag files.
        """
        
        rawdf = pd.read_csv(rawf, encoding='utf-8')
        lemdf = pd.read_csv(lemf, encoding='utf-8')
        
        return(rawdf, lemdf)
    
    def testalign(raw,lem,col="tagged_text"):
        """
        Make sure that the lemmatized texts align w/ originals.
        """
        
        testequal = raw[col] == lem[col]
        if sum(testequal) == len(raw):
            print("Files aligned")
        else:
            raise(AssertionError)
            
            
    def appendsens(fulldf=None, rawdf=None):
        """
        Add individual senators to a master data frame.
        """
        if type(fulldf) == pd.core.frame.DataFrame:
            fulldf = fulldf.append(rawdf, ignore_index=True)
        else:
            fulldf = rawdf
            
        return fulldf
    
    
    
class topiclem:
    
    class Config:
        
        topicfile = "D:/cong_text/csvs/topics/ExpAgenda_topics_113.csv"
        taglemfile = "D:/cong_text/csvs/tagged/lemma_merged_id.csv"
        taglemcols = ['docid', 'tagged_text', 'lemma_text']
        howmerge = 'left'
        mergeon = 'docid'
        mergeoutpath = "D:/cong_text/final_pos/"
        mergeoutfile = "topic_lemtag_merged_113.csv"
        
        
    def loadtopiclem(topicfile, taglemfile):
        """
        Load topic and docid merged tag_lemma files.
        """
        
        topicdf = pd.read_csv(topicfile, encoding='utf-8')
        taglemdf = pd.read_csv(taglemfile, encoding='utf-8')
        
        return(topicdf, taglemdf)
    
    def mergetoplem(topicdf, taglemdf, taglemcols, howmerge, mergeon):
        """
        Merge the topic and docid merged tag_lemma dataframes.
        """
        
        taglemdf = taglemdf[taglemcols]
        merged = topicdf.merge(taglemdf, how=howmerge, on=mergeon)
        
        return merged
    
    def testmergelen(topicdf, merged):
        """
        Check that the merge worked successfully.
        """
        
        errors = []
        temp_lemtext = merged.lemma_text
        temp_lemtext.dropna(inplace=True)
        
        if len(topicdf) != len(merged):
            errors.append("The number of merged rows is incorrect")
        
        if len(topicdf) != len(temp_lemtext):
            lendiff = len(topicdf) - len(temp_lemtext)
            errors.append("{} rows are missing lemmatized and tagged text".format(lendiff))
            
        if len(errors) > 0:
            out = ' & '.join(errors)
            print(out)
            raise(AssertionError)
        else:
            print("Files successfully merged")
            
            
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
        


class newfeatures(object):
    
    def __init__(self):
        
        # from build object
        self._raw_feats = None
        self._raw_tags = None
        self._to_replace = None # sen specific n-grams
        self._replacements = None # sen specific placeholders
        
        # to create
        self._prpnum_feats = None
        self._vrbtense_feats = None
        self._nounnum_feats = None
        self._allnouns_feats = None
        self._nopropnouns_feats = None
        
        # constant compiled regex
        self._prpsing_re = re.compile("((?<=i)|(?<=(me|he|it|my))|" +
                                      "(?<=(she|him|her|his|its))|" +
                                      "(?<=(this|that|mine|hers))|" +
                                      "(?<=myself)|(?<=(himself|herself))|(?<=yourself))" +
									  "_PRP\$?")
        self._prpplur_re = re.compile("((?<=(we|us))|(?<=^our)|(?<=\sour)|" +
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
        
    
    def loadbuildobj(self, infile):
        
        with open(infile, "rb") as f:
            buildobj = pickle.load(f)
            
        self._raw_feats = buildobj.DTM_features
        self._raw_tags = buildobj.tagonly_features
        self._to_replace = buildobj.commonngrams_sens
        self._replacements = buildobj.sens_replacements
        
        
    def prp_num_sub(self, sing_re=None, plur_re=None):
        
        if sing_re is None:
            sing_re = self._prpsing_re
        if plur_re is None:
            plur_re = self._prpplur_re
        
        self._prpnum_feats = [re.sub(sing_re, '_PRPSING', feat) for feat in self._raw_feats]
        self._prpnum_feats = [re.sub(plur_re, '_PRPPLUR', feat) for feat in self._prpnum_feats]
        
    def replace_specific(self):
        
        for i in range(len(self._to_replace)):
            try:
                tempidx = self._prpnum_feats.index(self._to_replace[i])
            except ValueError:
                continue
            self._prpnum_feats[tempidx] = self._replacements[i]
        
        self._full_prpnum_feats = [i for i in self._prpnum_feats]
        self._prpnum_feats = [re.sub(self._gettags_re, '', feat) for feat in self._prpnum_feats]

    
    def verb_tense_sub(self, past_re=None, future_re=None):
        
        if past_re is None:
            past_re = self._past_re
        if future_re is None:
            future_re = self._future_re
        
        self._vrbtense_feats = [re.sub(past_re, 'VBPAST', feat) for feat in self._raw_tags]
        self._vrbtense_feats = [re.sub(future_re, 'VBFUT', feat) for feat in self._vrbtense_feats]
       
        
    def noun_num_sub(self, sing_re=None, plur_re=None):
        
        if sing_re is None:
            sing_re = self._nnsing_re
        if plur_re is None:
            plur_re = self._nnplur_re
            
        self._nounnum_feats = [re.sub(sing_re, 'NNSING', feat) for feat in self._prpnum_feats]
        self._nounnum_feats = [re.sub(plur_re, 'NNPLUR', feat) for feat in self._nounnum_feats]
        
       
        
    def noun_super_sub(self, nopropnoun_re=None):
        
        if nopropnoun_re is None:
            nopropnoun_re = self._nopropnouns_re
        
        self._nopropnouns_feats = [re.sub(nopropnoun_re, 'NOUN', feat) for feat in self._prpnum_feats]
        self._allnouns_feats = [re.sub(self._propnouns_re, 'NOUN', feat) for feat in self._nopropnouns_feats]
        
    
    def save(self, outfile):
        
        with open(outfile, "wb") as f:
            pickle.dump(self.__dict__, f, protocol=-1)

      
        

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
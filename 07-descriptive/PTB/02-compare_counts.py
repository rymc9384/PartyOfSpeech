# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 11:50:45 2018

@author: Ryan McMahon
"""

import argparse
import os
import pandas as pd
from utils import featureset, analysisutils


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Compare Senate and PTB-WSJ Corpora")
    parser.add_argument('--inptb', help="PTB DTM and vocab file", required=True, \
                        default="D:/cong_text/final_pos/ptb/ptb_dtm_vocab.pkl")
    parser.add_argument('--insenfeats', help="Senate vocab file", required=True, \
                        default="D:/cong_text/final_pos/DTMs/newfeatures_vocab.pkl")
    parser.add_argument('--insencounts', help="Senate party counts (topic 0)", \
                        required=True, default="D:/cong_text/final_pos/DTMs/party_counts_topic0.pkl")
    parser.add_argument('--outpath', help="Path to where to save output CSVs", \
                        required=True, default="D:/cong_text/final_pos/ptb/")

    ARGS = parser.parse_args()

    print("Initializing output dataframes and declaring constants...\n")
    comparisonSen = {'_prpnum_feats': ['PRPSING', 'PRPPLUR'],
                     '_vrbtense_feats': ['VBPAST', 'VBFUT'],
                     '_nounnum_feats': ['NNSING', 'NNPLUR'],
                     '_nopropnouns_feats': ['NOUN'],
                     '_allnouns_feats': ['NOUN']
                     }
    comparisonPTB = {'prpnum_feats': ['PRPSING', 'PRPPLUR'],
                     'vrbtense_feats': ['VBPAST', 'VBFUT'],
                     'nounnum_feats': ['NNSING', 'NNPLUR'],
                     'nopropnouns_feats': ['NOUNA'],
                     'allnouns_feats': ['NOUNB']
                     }

    outputTags = pd.DataFrame(columns = [v for k in comparisonPTB for v in comparisonPTB[k]])
    outputAll = {k: None for k in comparisonSen.keys()}


    print("Loading PTB Features and Counts...")
    ptb = featureset(featurefile=ARGS.inptb)
    ptb.loadself()

    print("Loading Senate Features and Counts...")
    sen = featureset(featurefile=ARGS.insenfeats, countsfile=ARGS.insencounts)
    sen.loadself()
    sen.loadcounts()


    print("Looping over feature sets...")
    for k in range(len(comparisonSen)):

        featsSen = list(comparisonSen.keys())[k]
        featsPTB = list(comparisonPTB.keys())[k]

        print("\nAnalyzing {}...".format(featsSen))

        ptb.builddf(sen=False, features=ptb.__dict__[featsPTB])
        sen.builddf(sen=True, features=sen.__dict__[featsSen])

        print("\tMerging PTB and Senate counts...")
        tmp_df = pd.merge(ptb.temp_df, sen.temp_df, how="outer", on="words", suffixes=['1','2'])
        tmp_df = tmp_df.replace(to_replace=pd.np.nan, value=0)
        tmp_df['priors1'] = 0.01
        tmp_df['priors2'] = 0.01

        print("\tRunning Fightin' Words...") # positive vals are associated w/ PTB
        a = analysisutils(wordcounts=tmp_df)
        a.fightinwords()

        outputAll[featsSen] = a._fwoutput

        for i,v in enumerate(comparisonSen[featsSen]):
            tmp_w = comparisonPTB[featsPTB][i]
            outputTags.loc[0,tmp_w] = a.get_word(word=v).zeta.values[0]
            outputTags.loc[1,tmp_w] = a.get_word(word=v).delta.values[0]
            outputTags.loc[2,tmp_w] = a.get_word(word=v)["count"].values[0]

    
    # add row names to `outputTags`
    outputTags.index = ["zeta", "delta", "count"]
    
    print("Saving outputs...")
    if not os.path.exists(ARGS.outpath):
        os.makedirs(ARGS.outpath)

    for k in outputAll:
        tmp = outputAll[k]
        outfile = ARGS.outpath + 'all_PTB114zetas_' + k + '.csv'
        tmp.to_csv(outfile, index=False, encoding='utf-8')
        print("\t{} saved...".format(outfile))

    outfile = ARGS.outpath + 'tags_PTB114zetas.csv'
    outputTags.to_csv(outfile, index=True, encoding='utf-8')
    print("\t{} saved...".format(outfile))

    print("\nDONE!")

# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 09:24:17 2017

@author: Ryan McMahon
"""

import argparse
import os
import pandas as pd

from utils import featureset, datautils, analysisutils


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Conduct intra- and inter-topic analyses")
    parser.add_argument('--infeatures', help="Features object file", required=True, \
                        default="D:/cong_text/final_pos/DTMs/newfeatures_vocab.pkl")
    parser.add_argument('--intopicpattern', help="Path with pattern for party topic counts", \
                        required=True, default="D:/cong_text/final_pos/DTMs/party_counts*")
    parser.add_argument('--outpath', help="Path to where to save output CSVs", \
                        required=True, default="D:/cong_text/final_pos/analysis/")

    ARGS = parser.parse_args()

    
    print("Initializing output dataframes and declaring constants...\n")
    comparisons = {
                '_prpnum_feats': ['PRPSING', 'PRPPLUR'],
                '_vrbtense_feats': ['VBPAST', 'VBFUT'],
                '_nounnum_feats': ['NNSING', 'NNPLUR']
              }
    output = {k: pd.DataFrame(columns = ['topic'] + comparisons[k]) for k in comparisons.keys()}
    
    print("Loading feature sets...\n")
    feats = featureset(featurefile = ARGS.infeatures)
    feats.loadself()
  
    print("Finding all party topic count files...\n")
    d = datautils(countspathpattern = ARGS.intopicpattern)
    
    # loop over all topic party counts
    for i in range(45 + 1):
        
        print("Loading party counts for topic {}...".format(i))
        d.load_counts(topic = i)
        
        for k in comparisons.keys():
            
            print("\tAnalyzing {}...".format(k))
            d._features = feats.__dict__[k]
            d.builddf()
            a = analysisutils(wordcounts=d._tempdf)
            a.fightinwords()
            
            for v in comparisons[k]:
                output[k].loc[i,v] = a.get_word(word=v).zeta.values[0]
                
            output[k].topic[i] = i
            
        print("\n")
        
        
    print("Saving outputs...")
    if not os.path.exists(ARGS.outpath):
        os.makedirs(ARGS.outpath)
        
    for k in output.keys():
        tmp = output[k]
        outfile = ARGS.outpath + '113zetas' + k + '.csv'
        tmp.to_csv(outfile, index=False, encoding='utf-8')
        print("\t{} saved...".format(outfile))
        
    print("\nDONE!")
    
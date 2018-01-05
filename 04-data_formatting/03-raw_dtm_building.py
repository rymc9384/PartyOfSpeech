# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 13:04:14 2017

@author: Ryan McMahon
"""

import argparse
import os
import pickle
import re
import pandas as pd

from utils import buildrawdtm


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Generate raw DTM and feature sets")
    parser.add_argument('--infile', help="Topic/lemtag merged CSV file", required=True, \
                        default="D:/cong_text/final_pos/topic_lemtag_merged_114.csv")
    parser.add_argument('--outpath', help="Path to output directory", required=True, \
                        default="D:/cong_text/final_pos/TDMs/")
    parser.add_argument('--outfile', help="Filename for the raw DTM and vocab", \
                        required=True, default="raw_dtmbuildobj.pkl")

    ARGS = parser.parse_args()

    print("Reading in merged data...\n")
    merged = pd.read_csv(ARGS.infile, encoding='utf-8')

    print("Removing newline symbols...\n")
    merged['lemma_text'] = [re.sub("[\n]", "", merged.lemma_text[i]) for i in range(len(merged))]

    sens = list(merged.senator.unique())
    nsens = len(sens)

    dtmbuild = buildrawdtm()

    print("Looping over individual senators...")
    for i, sen in enumerate(sens):
        print("Getting common ngrams for {}... \t {}/{}".format(sen, i+1, nsens))
        sendf = merged[merged.senator == sen]
        sentext = list(sendf.lemma_text)

        dtmbuild.get_commonngrams(text=sentext, general=False)


    print("\nGetting common ngrams for all senators...\n")
    dtmbuild.get_commonngrams(text=list(merged.lemma_text), general=True)

    print("Getting rare ngrams for all senators...\n")
    dtmbuild.get_rarengrams(text=list(merged.lemma_text))

    print("Making senator and general common n-gram lists mutually exclusive...\n")
    dtmbuild.make_exclusive_commonngrams()

    print("Making replacement features:")
    print("\tfor general common n-grams...")
    dtmbuild.make_replacement_feats(which='general')
    print("\tfor senator specific common n-grams...")
    dtmbuild.make_replacement_feats(which='sens')
    print("\tfor rare n-grams...\n")
    dtmbuild.make_replacement_feats(which='rare')

    print("Building full DTM...\n")
    dtmbuild.fit_transformfull(text=list(merged.lemma_text))

    print("Getting tag-only feature set...\n")
    dtmbuild.get_tagsonly()

    print("Saving raw DTM and feature names...")
    if os.path.exists(ARGS.outpath) == False:
        os.makedirs(ARGS.outpath)
    dtmoutfile = ARGS.outpath + ARGS.outfile
    
    with open(dtmoutfile, "wb") as f:
        pickle.dump(dtmbuild, f, protocol=-1)

    print("Done!")

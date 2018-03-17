# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 09:47:40 2018

@author: Ryan McMahon
"""

import argparse
import os
import numpy as np
import pandas as pd
import pickle

if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Conduct intra- and inter-topic analyses")
    parser.add_argument('--insen', help="Topic/lemtag merged CSV file", required=False, \
                            default="D:/cong_text/final_pos/topic_lemtag_merged_114.csv")
    parser.add_argument('--inzetas', help="Features object file", required=False, \
                        default="D:/cong_text/final_pos/DTMs/zetas_vector.pkl")
    parser.add_argument('--indtmbuild', help="Raw DTM build pkl file", required = False, \
                        default="D:/cong_text/final_pos/DTMs/raw_dtmbuildobj.pkl")
    parser.add_argument('--outmerged', help="Doc meta data and fw_scores file", required = False, \
                        default="D:/cong_text/final_pos/topic_fwscore_merged114.csv")
    ARGS = parser.parse_args()

    print("Reading in Topic/lemtag Merged CSV File...")
    df = pd.read_csv(ARGS.insen)

    print("Removing text from `insen' dataframe...\n")
    df = df[df.columns[:-2]]

    print("Reading in zetas...")
    with open(ARGS.inzetas, "rb") as f:
        zetas = pickle.load(f)


    print("Reading in DTM build...")
    with open(ARGS.indtmbuild, "rb") as f:
        rawbuild = pickle.load(f)

    print("Subsetting build to just DTM and clearing memory...\n")
    DTM = rawbuild.DTM
    del rawbuild

    print("Scaling documents...\n")
    scaled_docs = DTM.dot(zetas)

    print("Merging doc scores to topic/lemtag merged dataframe...\n")
    df['fw_scale'] = scaled_docs

    print("Saving merged doc scores to {}\n".format(ARGS.outmerged))
    df.to_csv(ARGS.outmerged, index=False, encoding='utf-8')

    print("DONE!")

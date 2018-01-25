# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 11:37:29 2018

@author: Ryan McMahon
"""

import argparse
import os
import pandas as pd

from utils import cleanptb


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Build feature counts for PTB WSJ sample")
    parser.add_argument('--outpath', help="Path to where to save output pkl", \
                        required=True, default="D:/cong_text/final_pos/ptb/")
    parser.add_argument('--outfile', help="What to name PTB feature object", \
                        required=True, default="ptb_dtm_vocab.pkl")

    ARGS = parser.parse_args()
    
    # initialize object
    ptbbuild = cleanptb()
    
    # get nltk data and format
    ptbbuild.format_nltk_data()

    # build dtm
    ptbbuild.fit_dtm()

    # make feature sets
    ptbbuild.makefeats()

    # make outpath if necessary
    if not os.path.exists(ARGS.outpath):
        os.makedirs(ARGS.outpath)
    outfile = ARGS.outpath + ARGS.outfile
    
    # save object
    ptbbuild.save(outfile=outfile)
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 10:00:04 2017

@author: Ryan McMahon
"""

import argparse
import os
import pandas as pd

from glob import glob


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Format Tagged Text for Lemmatization with Morpha")
    parser.add_argument('-i', '--inpath', help="path to tagged text CSVs (from `01-fix_parentheses.py`)", required=True)
    parser.add_argument('-op', '--outpath', help="Where to save output", required=True)
    
    ARGS = parser.parse_args()
    
    if os.path.exists(ARGS.outpath) == False:
            os.makedirs(ARGS.outpath)
    
    infiles = glob(ARGS.inpath+"*.csv")
    
    for infile in infiles:
        df = pd.DataFrame.from_csv(infile, encoding="utf-8")
        texts = list(df.tagged_text)
        
        inname = infile.split('\\')[1]
        outname = "{}{}.tag".format(ARGS.outpath, inname[:-4])
        
        with open(outname, "w", encoding="utf-8") as outfile:
            outfile.write("\n".join(texts))
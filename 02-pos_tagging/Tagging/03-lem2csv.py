# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 11:39:28 2017

@author: Ryan McMahon
"""

import argparse
import os
import pandas as pd

from glob import glob



if __name__ == "__main__":

    # parse command line args:
    parser = argparse.ArgumentParser(description="Format Tagged Text for Lemmatization with Morpha")
    parser.add_argument('--inpathcsv', help="path to tagged text CSVs (from `01-fix_parentheses.py`)", required=True)
    parser.add_argument('--inpathlem', help="path to lemmatized texts (from Morpha transformation)", required=True)
    parser.add_argument('-op', '--outpath', help="Where to save output", required=True)

    ARGS = parser.parse_args()

    # create outpath directory if necessary:
    if os.path.exists(ARGS.outpath) == False:
            os.makedirs(ARGS.outpath)

    # find all input csvs
    incsvs = glob(ARGS.inpathcsv + "*.csv")

    # loop over senators' csvs:
    for incsv in incsvs:

        # get the file name w/o the path:
        inname = incsv.split('\\')[1]
        # translate to lemmatized file name:
        inlem = "{}{}.lem".format(ARGS.inpathlem, inname[:-4])

        # read in data:
        df = pd.DataFrame.from_csv(incsv, encoding="utf-8")

        with open(inlem, 'r', encoding="utf-8") as f:
            lemmatized = f.readlines()

        # merge in lemmatized text:
        df['lemma_text'] = lemmatized

        # write out data:
        outname = "{}{}".format(ARGS.outpath, inname)
        df.to_csv(outname, index=False, encoding="utf-8")
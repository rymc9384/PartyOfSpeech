# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 11:40:21 2017

@author: Ryan McMahon
"""

import argparse
import os

from glob import glob
from utils import Config, preprocessfile, preprocesscombined
from utils import mergecombinedinfo


if __name__ == "__main__":
    
    # Parsing arguments:
    parser = argparse.ArgumentParser(description="Process Tokenized Text for ExpressedAgenda topic model")
    parser.add_argument('--min-date', help="Earliest date for press release to be included in processing. E.g., '2013-01-03'", required=False, default=None)
    parser.add_argument('--max-date', help="Latest date for press release to be included in processing. E.g., '2013-01-02'", required=False, default=None)
    parser.add_argument('-o', '--outfile', help="Filename for the output", required=True)

    ARGS = parser.parse_args()
    
    badvocab = None
    df_all = None
    files = glob(Config.inpath + "*.csv")
    
    print("Processing the individual files...\n")
    
    for i, file in enumerate(files):
        print("\t{}: Processing {}...".format(i, file))
        df_all, badvocab = preprocessfile(file, df_all, badvocab, \
                                          ARGS.min_date, ARGS.max_date)
        
    text = list(df_all.topic_text)
    text = preprocesscombined(text, badvocab)
    df_all.topic_text = text
    
    # Merge with senator info:
    print("\nMerging text with Senator info...")
    df_all = mergecombinedinfo(df_all=df_all, infofile=Config.senatorinfo)
    
    # Save the combined texts:
    print("\nSaving combined texts...")
    if os.path.exists(Config.outpath) == False:
        os.makedirs(Config.outpath)
        
    outfile = Config.outpath + ARGS.outfile
    df_all.to_csv(path_or_buf=outfile, index=False, encoding='utf-8')
    print("\nDONE!")
    
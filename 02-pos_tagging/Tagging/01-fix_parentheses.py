# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 10:34:06 2017

@author: Ryan McMahon
"""

import os
import re
import pandas as pd

from glob import glob


os.chdir('D:/cong_text/csvs/tagged/raw/')

outpath = 'D:/cong_text/csvs/tagged/fixedparenths/'

leftparenth = re.compile('(?<=\(_)[A-Z]{2,4}')
rightparenth = re.compile('(?<=\)_)[A-Z]{2,4}')


def fix_parenths(df):
    # df = (pd.DataFrame) dataframe w/ tagged text; produced by `00-nltk_tagging.py`
    fixed_texts = []
    
    for text in df.tagged_text:
        text = re.sub(leftparenth, '(', text)
        text = re.sub(rightparenth, ')', text)
        
        fixed_texts.append(text)
    
    return(fixed_texts)



if __name__ == "__main__":
    
    if os.path.exists(outpath) == False:
        os.mkdir(outpath)
    
    files = glob("*.csv")
    
    for file in files:
        df = pd.read_csv(file)
        df.tagged_text = fix_parenths(df)
        
        outfile = outpath + file
        
        df.to_csv(path_or_buf=outfile, index=False, encoding='utf-8')
        
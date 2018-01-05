# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 12:24:31 2017

@author: Ryan McMahon
"""

import os
import locale

from datetime import datetime


class Config(object):
    # Configurations for tagging with NLTK

    tagger = "D:/Downloads/stanford-postagger-full-2017-06-09/models/wsj-0-18-bidirectional-distsim.tagger"
    jar = "D:/Downloads/stanford-postagger-full-2017-06-09/stanford-postagger.jar"
    pathinput = "D:/cong_text/csvs/"
    tokenout = "D:/cong_text/csvs/tokenized/raw/"
    taggedout = "D:/cong_text/csvs/tagged/raw/"

    def java_home():
        # define an environment variable directing to java
        os.environ.update({"JAVAHOME":"C:/Program Files/Java/jdk1.8.0_131/bin"})

    def fix_heller_dates(df):
        # df = pd.DataFrame w/ named columns
        locale.setlocale(locale.LC_ALL, 'esp_esp')
        tofix = df['form_date'] == "CHECK"
        tofix = list(tofix.where(tofix==True).dropna().index)

        for t in tofix:
            date = df.post_date.loc[t]
            date = datetime.strptime(date, '%d de %B de %Y')
            date = date.strftime('%Y-%m-%d')
            df.form_date.loc[t] = date

        return(df)

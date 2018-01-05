# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 14:51:57 2017

@author: Ryan McMahon
"""

import argparse
import os
import pandas as pd
from glob import glob

if __name__ == "__main__":

    # Parsing arguments:
    parser = argparse.ArgumentParser(description="Extract and clean text from a Senator's press releases")
    parser.add_argument('-hp', '--html-path', help="File path to HTML folders", required=True)
    parser.add_argument('-n', '--number', help="Number associated with relevant extraction script", required=True)
    parser.add_argument('-o', '--output', help="Output path", required=True)
    parser.add_argument('-rmpp', '--rmprepost', help="(y) or (n); Remove pre/post of main text", required = True)
    parser.add_argument('-rmq', '--rmquotes', help="(y) or (n); Remove quotation marks in text", required = True)

    ARGS = parser.parse_args()


    # Find and execute senator specific extraction/cleaning script:
    scripts = glob("*.py")
    script = scripts[int(ARGS.number)]

    with open(script,encoding='utf-8') as source_file:
        exec(source_file.read())


    # Make senator specific functions executable:
    l = []
    try:
        for key, val in locals().items():
            if callable(val) and val.__module__ == __name__:
                l.append(key)
    except RuntimeError:
        for key, val in locals().items():
            if callable(val) and val.__module__ == __name__:
                l.append(key)

    extract = locals()[l[0]]
    clean = locals()[l[1]]

    # Find the relevant HTML files:
    os.chdir(ARGS.html_path)
    folders = glob("*")
    files = glob(folders[int(ARGS.number)] + "/*.htm")

    # Extract the text from the HTMLS:
    print("Extracting text...\n")
    results = []
    for file in files:
        results.append(extract(file))

    # Clean the extracted text:
    if ARGS.rmprepost == "y":
        rm_prepost = True
    else:
        rm_prepost = False

    if ARGS.rmquotes == "y":
        rm_quotes = True
    else:
        rm_quotes = False
		
    print("Cleaning text...\n")
    for result in results:
        result.append(clean(result[5], rm_prepost, rm_quotes))

    # Put into a pandas dataframe and write to CSV:
    print("Saving data...\n")
    df = pd.DataFrame(results)
    df.columns = ['docid', 'senator', 'post_date', 'form_date', \
                  'title', 'raw_text', 'clean_text']

    try:
        os.chdir(ARGS.output)
    except FileNotFoundError:
        os.mkdir(ARGS.output)
        os.chdir(ARGS.output)

    file_out = ARGS.number + '-' + df.senator[0] + '.csv'
    df.to_csv(path_or_buf=file_out, index=False)

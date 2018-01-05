# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 10:40:29 2017

@author: Ryan McMahon
"""

import os
import re
from bs4 import BeautifulSoup
from glob import glob

from utils import text_cleaning

regex_months = text_cleaning.regex_months
dc_dateline = text_cleaning.dc_dateline

os.chdir('D:/cong_text/htmls/')

########################
### 81) Senator Schatz:
    
files = glob('./schatz/*.htm')

# Extract text from Schatz's pages:
def extract_html_81(file):
    
    ###########################################################################   
    # - PURPOSE: Extract text from Senator Schatz's press release HTMLs.
    #
    # - ARGUMENT(S): 
    #   1) file, (str) = file path for a single HTML page
    #                
    # - OUTPUT: (list) = [docid, senator, postDate, formattedDate, title, text]
    ###########################################################################

    # Extract basics from file name:
    docid = file.split('\\')[1][:-4]
    sen = re.search('[a-z]+', docid).group()
    
    # Read in the press release:
    with open(file, 'rb') as f:
        html = f.read()
    soup = BeautifulSoup(html, "lxml")
    
    # Dealing with line breaks that mess up spacing:
    for br in soup.find_all("br"):
        br.replace_with("\n")
    
    # Extract the title:
    title = soup.find('h1',{"class":"entry-title"})
    if title:
        title = title.get_text()
    else:
        return([docid, sen] + ['']*4)
    
    title = re.sub('“|”', '', title)
    title = title.strip()

    # Extract the date posted:
    post_date = soup.find('time',{"class":"dateline"})
    date_mark = post_date.get_text()
    post_date = post_date.attrs['datetime']
    
    # Format the date:
    form_date = post_date
    
    # Grab the text:
    main = soup.find('div',{"id":"main_column"})
    
    contents = main.get_text()
    
    # Collapse newlines:
    contents = re.sub(r'\n', ' ', contents)
    
    # Format whitespace:
    contents = re.sub("\s+", ' ', contents)
    
    # get rid of stuff up to the posted date:
    contents = re.sub('^.*?' + date_mark, '', contents)
    
    # cut off code at the end (if there):
    contents = re.sub('\/\/ cribbed.*?$','', contents)
    
    # Cleanup whitespace at start and end:
    contents = contents.strip()
    
    # Put it all into a list:
    out = [docid, sen, post_date, form_date, title, contents]
    
    return(out)


def clean_text_81(text, rm_prepost=True, rm_quotes=False):
    
    ###########################################################################   
    # - PURPOSE: Clean text extracted from Schatz's press releases.
    #
    # - ARGUMENT(S): 
    #   1) text, (str) = Text extracted from the HTML (see above)
    #   2) rm_prepost, (bool) = Remove extra text (before dateline, after end);
    #                           default=True
    #   3) rm_quotes, (bool) = Remove quotation marks from the text; 
    #                           default=False
    #                
    # - OUTPUT: (str) = Text
    #
    ###########################################################################
    
    # Replace phone numbers with a placeholder.
    text = re.sub("(1-)?(\(?\d{3}\)?-*\s*|\(?xxx\)?-*\s*)?(\d{3}|xxx)-*\s*(\d{4}|xxxx)", \
                  "this number", text)   
    
    # Format quotation/apostrophe marks:
    text = re.sub('“|”', '"', text)
    text = re.sub('’|‘', "'", text)
    
    # Format dashes:
    text = re.sub('–+|—+|-+', " - ", text) # guarantee spacing for dateline
    
    text = re.sub(r'\xad', '', text)
    text = re.sub('\s+', ' ', text)
    text = re.sub("\*+", "", text)
    text = re.sub("·+", "", text)
    
    text = re.sub("Hawai('|\?)i", "Hawaii", text)
    
    text = text.strip()
    
    # If removing text through dateline and junk at the end
    if rm_prepost:
        
        # First just toss all the location lines
        text = re.sub("^" + dc_dateline + "(\s+\(.*?\)){0,1}\s+-\s+(?=[A-Z])", "", text)
        text = re.sub("^(D\.C\.|D\.C|DC).*?\s+-\s+(?=[A-Z])", "", text)
        text = re.sub("^([A-Za-z]*[\s]{0,1}){1,4}\,*\s*(HI|HAWAII|Hawaii)\s+\-\s+(?=[A-Z])", \
                      "", text)        
        text = re.sub("^.*?HONOLULU\s+-\s+(?=[A-Z])", "", text)
        
        # Trouble maker:
        text = re.sub("^By Sen\. .*?\:\s+(?=[A-Z])", "", text)
        
        # look for the text at the end using the octothorpe/pound sign
        post = re.search("-?(###|#\s#\s#).*?$", text)
        
        # if we find something, run diagnostics again
        if post:
            post_span = post.span()
            post_len = post_span[1] - post_span[0]
            post_frac = post_len / len(text)
                
            # if 'post' comprises less than 15% of full text, remove it
            # (these tend to be much shorter, thus the smaller cutoff)
            if post_frac < 0.15:
                text = text[:post_span[0]]
                
        text = text.strip()
        
    return(text)
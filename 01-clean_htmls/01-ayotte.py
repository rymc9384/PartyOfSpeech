# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 11:09:32 2017

@author: Ryan McMahon
"""

# LAST EDITED: 08/30/2017


import os
import re
from bs4 import BeautifulSoup
from glob import glob
from datetime import datetime

from utils import text_cleaning

regex_months = text_cleaning.regex_months
dc_dateline = text_cleaning.dc_dateline

os.chdir('D:/cong_text/htmls/')

########################
### 1) Senator Ayotte:
    
files = glob('./ayotte/*.htm')

# Extract text from Ayotte's pages:
def extract_html_1(file):
    
    ###########################################################################   
    # - PURPOSE: Extract text from Senator Ayotte's press release HTMLs.
    #
    # - ARGUMENT(S): 
    #   1) file, (str) = file path for a single HTML page
    #                
    # - OUTPUT: (list) = [docid, senator, postDate, formattedDate, title, text]
    # 
    # - NOTES: 
    #       07/24/17) './ayotte/280ayotte.htm is an empty file'.
    #
    ###########################################################################

    # Extract basics from file name:
    docid = file.split('\\')[1][:-4]
    sen = re.search('[a-z]+', docid).group()
    
    # Read in the press release:
    with open(file, 'rb') as f:
        html = f.read()
    soup = BeautifulSoup(html, "lxml")
    
    # this is to deal with the empty file:
    if len(soup) == 0:
        return([docid, sen] + ['']*4)
        
    
    # Dealing with line breaks that mess up spacing:
    for br in soup.find_all("br"):
        br.replace_with("\n")
    
    # Extract the title and date:
    title = soup.find('h1',{"class":"fancy_font"}).get_text()
    title = re.sub('“|”', '', title)
    post_date = soup.find('div',{"class":"inner-lyt-dates"}).get_text()
    post_date = re.sub('\n|\t', '', post_date)
    
    # Format the date:
    form_date = datetime.strptime(post_date, '%b %d, %Y')
    form_date = '{}-{}-{}'.format(form_date.year, form_date.month, form_date.day)
    
    # Grab the text:
    contents = soup.find('div',{'class':'bd record-bd'}).get_text()
    
    # Collapse newlines:
    contents = re.sub(r'\n', ' ', contents)
    
    # Format whitespace:
    contents = re.sub("\s+", ' ', contents)
    
    # Cleanup whitespace at start and end:
    contents = contents.strip()
    
    # Put it all into a list:
    out = [docid, sen, post_date, form_date, title, contents]
    
    return(out)


def clean_text_1(text, rm_prepost=True, rm_quotes=False):
    
    ###########################################################################   
    # - PURPOSE: Clean text extracted from Ayotte's press releases.
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
    text = re.sub("(1-)?(?:\(?\d{3}\)?-*\s*|\(?xxx\)?-*\s*)(\d{3}|xxx)-*\s*(\d{4}|xxxx)", \
                  "this number", text)   
    
    # Format quotation/apostrophe marks:
    text = re.sub('“|”', '"', text)
    text = re.sub('’', "'", text)
    
    # Format dashes:
    text = re.sub('–+|—+|-+', " - ", text)
    text = re.sub('\s+', ' ', text)
    
    # Get rid of the asterisk bullet points:
    text = re.sub("\*+", "", text)
    
    # Clean leading/trailing whitespace
    text = text.strip()
    
    # If removing text through dateline and junk at the end
    if rm_prepost:
        
        # First just toss all the location lines
        text = re.sub("^" + dc_dateline + ".*?(?=[A-Z])", "", text)
        text = re.sub("^(D\.C\.|D\.C|DC).*?(?=[A-Z])", "", text)
        text = re.sub("^\([A-Za-z]{3,}.*?\)\s+-\s+(?=[A-Z])", "", text)
        text = re.sub("^(N\.H\.|NH)\s+-\s+(?=[A-Z])", "", text)
        
        # look for the dateline using dates
        pre = re.search("^.*?" + regex_months + \
                        "\s+\d{1,2}(?:(\,\s+\d{4}\s+-\s+)|" + \
                        "(\s+-\s+))(?=[A-Z])", text)
        
        # if we don't find anything, look for the dateline using all caps
        if pre == None:
            pre = re.search("^.*?[A-Z]{4,}\s+-\s+(?=[A-Z])", text)
        
        # if either of those turns up a match, do some diagnostics
        if pre:
            pre_span = pre.span()
            pre_len = pre_span[1] - pre_span[0]
            pre_frac = pre_len / len(text)
            
            # if 'pre' comprises less than 25% of full text, remove it
            if pre_frac < 0.25:
                text = text[pre_span[1]:]
        
        
        # look for the text at the end using the octothorpe/pound sign
        post = re.search("(###|#\s#\s#).*?$", text)
        
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
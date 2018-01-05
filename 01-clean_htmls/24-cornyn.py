# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 10:31:08 2017

@author: Ryan McMahon
"""


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
### 24) Senator Cornyn:
    
files = glob('./cornyn/*.htm')

# Extract text from Cornyn's pages:
def extract_html_24(file):
    
    ###########################################################################   
    # - PURPOSE: Extract text from Senator Cornyn's press release HTMLs.
    #
    # - ARGUMENT(S): 
    #   1) file, (str) = file path for a single HTML page
    #                
    # - OUTPUT: (list) = [docid, senator, postDate, formattedDate, title, text]
    #
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
        
    # Subset to area of interest:
    soup = soup.find('div', {"class":"col-sm-9 services-content main-content"})
    
    if soup == None:
        return([docid, sen] + ['']*4)
    
    # Extract the title:
    title = soup.find('h3')
    if title:
        title = title.get_text()
    else:
        return([docid, sen] + ['']*4)
    
    title = re.sub('“|”', '', title)
    title = title.strip()

    # Extract the date posted:
    post_date = soup.find('div',{"class":"col-sm-6"})
    if post_date:
        post_date = post_date.get_text()
    else:
        return([docid, sen,title] + ['']*3)
    
    post_date = re.sub("\s+", ' ', post_date)
    post_date = re.sub('^.*(?= [0-9]{1,2}\/)', '', post_date)
    post_date = post_date.strip()
    # Format the date:
    form_date = datetime.strptime(post_date, '%m/%d/%Y')
    form_date = '{}-{}-{}'.format(form_date.year, form_date.month, form_date.day)
    
    
    # Grab the text:
    contents = soup.find('div',{"class":"field field-name-body field-type-text-with-summary field-label-hidden"})
    if contents:
        contents = contents.get_text()
    else:
        contents = ""
    # Collapse newlines:
    contents = re.sub(r'\n', ' ', contents)
    
    # Format whitespace:
    contents = re.sub("\s+", ' ', contents)
    
    # Cleanup whitespace at start and end:
    contents = contents.strip()
    
    # Put it all into a list:
    out = [docid, sen, post_date, form_date, title, contents]
    
    return(out)


def clean_text_24(text, rm_prepost=True, rm_quotes=False):
    
    ###########################################################################   
    # - PURPOSE: Clean text extracted from Cornyn's press releases.
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
    text = re.sub('–+|—+|-+', " - ", text) # guarantee spacing for dateline
    text = re.sub('\s+', ' ', text)
    
    text = re.sub("\*+", "", text)
    text = text.strip()
    
    # If removing text through dateline and junk at the end
    if rm_prepost:
        
        # First just toss all the location lines (from older releases)
        text = re.sub("^.*?" + dc_dateline + "\s+-\s+(?=[A-Z])", "", text)
        text = re.sub("^(D\.C\.|D\.C|DC).*?(?=[A-Z])", "", text)
        text = re.sub("^(D\.C\.|D\.C|DC)\s+-\s+", "", text)

        text = re.sub("^.*?[A-Za-z]*\,*\s*(TX|TEXAS|Texas)\s+-\s+(?=[A-Z])", "", text)

        # look for the dateline using dates
        pre = re.search("^.*?" + regex_months + \
                        "\s+\d{1,2}(?:\,\s+\d{4}http.*?\.[a-z]{3,4})" + \
                        "(?=[A-Z])", text)
        
        # if we don't find anything, look for the dateline using all caps
        if pre == None:
            pre = re.search("^.*?[A-Za-z]{4,}\, \s+-\s+(?=[A-Z])", text)
        
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
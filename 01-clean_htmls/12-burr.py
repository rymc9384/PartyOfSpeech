# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 15:29:22 2017

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
### 12) Senator Burr:
    
files = glob('./burr/*.htm')

# Extract text from Burr's pages:
def extract_html_12(file):
    
    ###########################################################################   
    # - PURPOSE: Extract text from Senator Burr's press release HTMLs.
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
        
    # Subset to where all the text is:
    soup = soup.find('div', {"id":"press"})
    if soup == None:
        return([docid, sen] + ['']*4)
    
    # Extract the title:
    title = soup.find('h1',{"class":"main_page_title"}).get_text()
    title = re.sub('“|”', '', title)
    title = title.strip()
    
    subtitle = soup.find('h2',{"class":"subtitle"})

    # Extract the date posted:
    post_date = soup.find('span',{"class":"date black"}).get_text()
    
    # Format the date:
    form_date = datetime.strptime(post_date, '%m.%d.%y')
    form_date = '{}-{}-{}'.format(form_date.year, form_date.month, form_date.day)
    
    
    # Grab the text:
    contents = soup.get_text()
    
    # Remove date:
    contents = re.sub('^\n'+post_date, '', contents)
    
    
    title_search = ' '.join(title.split(' ')[-5:]) + '\n'
    if subtitle:
        subtitle = subtitle.get_text().split('\n')
        if len(subtitle[0]) == 0:
            subtitle = subtitle[1]
        else:
            subtitle = subtitle[0]
        to_rm = re.search(subtitle, contents)
    else:
        to_rm = re.search(title_search, contents)
        
    if to_rm:    
        contents = contents[to_rm.end():]

    # Collapse newlines:
    contents = re.sub(r'\n', ' ', contents)
    
    # Format whitespace:
    contents = re.sub("\s+", ' ', contents)
    
    # Cleanup whitespace at start and end:
    contents = contents.strip()
    
    # Put it all into a list:
    out = [docid, sen, post_date, form_date, title, contents]
    
    return(out)


def clean_text_12(text, rm_prepost=True, rm_quotes=False):
    
    ###########################################################################   
    # - PURPOSE: Clean text extracted from Burr's press releases.
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
        text = re.sub("^" + dc_dateline + ".*?(?=[A-Z])", "", text)
        text = re.sub("^(D\.C\.|D\.C|DC).*?(?=[A-Z])", "", text)
        text = re.sub("^[A-Z]*\,*\s*(OH|Ohio)\s+-\s+", "", text)

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
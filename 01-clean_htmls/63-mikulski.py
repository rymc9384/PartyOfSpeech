# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 14:54:40 2017

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
### 63) Senator Mikulski:
    
files = glob('./mikulski/*.htm')

# Extract text from Mikulski's pages:
def extract_html_63(file):
    
    ###########################################################################   
    # - PURPOSE: Extract text from Senator Mikulski's press release HTMLs.
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
    title = soup.find('h1',{"class":"main_page_title"})
    if title:
        title = title.get_text()
    else:
        return([docid, sen] + ['']*4)
    title = re.sub('“|”', '', title)
    title = title.strip()
    

    # Extract the date posted:
    post_date = soup.find('time',{"class":"dateline"}).get_text()
    post_date = re.search('[A-Za-z]+ \d{1,2}\, \d{4}$', post_date)
    post_date = post_date.group()
    
    # Format the date:
    form_date = datetime.strptime(post_date, '%B %d, %Y')
    form_date = '{}-{}-{}'.format(form_date.year, form_date.month, form_date.day)
    
    # Grab the text:
    main = soup.find('div',{"id":"main_column"})
    pars = main.find_all('p')
        
    contents = [p.get_text() for p in pars]
    contents = ' '.join(contents)

    # Collapse newlines:
    contents = re.sub(r'\n', ' ', contents)
    
    # Format whitespace:
    contents = re.sub("\s+", ' ', contents)
    
    # Cleanup whitespace at start and end:
    contents = contents.strip()
    
    # Put it all into a list:
    out = [docid, sen, post_date, form_date, title, contents]
    
    return(out)


def clean_text_63(text, rm_prepost=True, rm_quotes=False):
    
    ###########################################################################   
    # - PURPOSE: Clean text extracted from Mikulski's press releases.
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
    
    # Fix `U. S.`
    text = re.sub('\s+U\. S\.(?=\s+)', r' U.S.', text)
    # Format dashes:
    text = re.sub('–+|—+|─+|-+', " - ", text) # guarantee spacing for dateline    
    text = re.sub('\s+', ' ', text)
    
    text = re.sub("\*+", "", text)
    text = text.strip()
    
    # If removing text through dateline and junk at the end
    if rm_prepost:
        
        # First just toss all the location lines
        text = re.sub("^" + dc_dateline + "\s+\-\s+(?=[A-Z])", "", text)
        text = re.sub("^(D\.C\.|D\.C|DC)\s+\-\s+(?=[A-Z])", "", text)
        text = re.sub("^[A-Za-z]*\s*[A-Za-z]*\,*\s*(Md\.|MD|Maryland)\s+-\s+(?=[A-Z])", "", text)
        text = re.sub("^([A-Za-z]*[\,]{0,1}[\s]{0,1}){1,4}\s+-\s+(?=(\"|[A-Z]))", "", text)
        
        text = re.sub("^" + regex_months + \
                        "\s+\d{1,2}(\,\s+\d{4})?" + \
                        "\s+-\s+(?=[A-Z])", "", text)
        
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
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:11:12 2017

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
### 53) Senator Leahy:
    
files = glob('./leahy/*.htm')

# Extract text from Leahy's pages:
def extract_html_53(file):
    
    ###########################################################################   
    # - PURPOSE: Extract text from Senator Leahy's press release HTMLs.
    #
    # - ARGUMENT(S): 
    #   1) file, (str) = file path for a single HTML page
    #                
    # - OUTPUT: (list) = [docid, senator, postDate, formattedDate, title, text]
    #
    # maybe the least consistent formatting of anyone...
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
    soup1 = soup.find('div', {"id":"press"})
    
    # if that doesn't work, it's an article and we need to adapt:
    if soup1 == None:
        soup1 = soup.find('div', {"id":"main_container"})
        
        if soup1 == None:
            return([docid, sen] + [""]*4)
        
        title = soup1.find('h1', {"class":"main_page_title"})
        if title:
            title = title.get_text()
        else:
            return([docid, sen] + [""]*4)
        
        if title == "Page Not Found":
            return([docid, sen] + [""]*4)
        
        title = re.sub('“|”', '', title)
        title = title.strip()
        
        post_date = soup1.find('time', {"class":"dateline"}).get_text()
        post_date = re.search('[A-Za-z]+ \d{1,2}\, \d{4}', post_date)
        post_date = post_date.group()
        
        form_date = datetime.strptime(post_date, '%B %d, %Y')
        form_date = '{}-{}-{}'.format(form_date.year, form_date.month, form_date.day)
        
        pars = soup1.find_all('p') 
        contents = [p.get_text() for p in pars]
        contents = ' '.join(contents)
    
    else:    
        soup = soup1
        
        # Extract the title:
        title = soup.find('h1', {"class":"main_page_title"}).get_text()
        title = re.sub('“|”', '', title)
        title = title.strip()
    
        # Extract the date posted:
        post_date = soup.find('span',{"class":"date black"}).get_text()
        
        # Format the date:
        form_date = datetime.strptime(post_date, '%m.%d.%y')
        form_date = '{}-{}-{}'.format(form_date.year, form_date.month, form_date.day)
        
        
        # Grab the text:
        pars = soup.find_all('p') 
        contents = [p.get_text() for p in pars]
        contents = ' '.join(contents)
        
        # sometime body of text is hidden in list items; 
        # this loses sentence order or removes the limited text from `pars`,
        # but this format seems rare (1/250 sample releases)
        lis = soup.find_all('li')
        if len(lis) > 0:
            li_contents = [l.get_text() for l in lis]
            li_contents = ' '.join(li_contents)
            
            # apply arbitrary cutoff for length distance
            if len(li_contents) > 2 * len(contents):
                contents = li_contents
            else:
                contents += ' ' + li_contents
    
    # Collapse newlines:
    contents = re.sub(r'\n', ' ', contents)
    
    # Format whitespace:
    contents = re.sub("\s+", ' ', contents)
    
    # Cleanup whitespace at start and end:
    contents = contents.strip()
    
    # Put it all into a list:
    out = [docid, sen, post_date, form_date, title, contents]
    
    return(out)


def clean_text_53(text, rm_prepost=True, rm_quotes=False):
    
    ###########################################################################   
    # - PURPOSE: Clean text extracted from Leahy's press releases.
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
    
    # Remove contact line:
    text = re.sub("^(Press\s+)?Contact.*?[0-9]{4}\s+(?=[A-Z])", "", text)
    
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
    text = re.sub("·+", "", text)
    text = text.strip()
    
    # If removing text through dateline and junk at the end
    if rm_prepost:
        
        # First just toss all the location lines 
        text = re.sub("^" + dc_dateline + "(\s+\(.*?\))?\s+\-\s+(?=[A-Z])", "", text)
        text = re.sub("^(D\.C\.|D\.C|DC)\s+\-\s+(?=[A-Z])", "", text)
        text = re.sub("^([A-Z]*[\s]{0,1}){1,4}\,*\s*(VT|VERMONT|Vermont|Vt\.)(\,?\s+[A-Z][a-z]{2,} \d{2})\s+-\s+(?=[A-Z])", "", text)
        
        # Dates at start:
        text = re.sub("^" + regex_months + \
                        "\s+\d{1,2}(\,\s+\d{4})?" + \
                        "\s+-\s+(?=[A-Z])", "", text)
        text = re.sub("^\(.*?" + regex_months + \
                        "\s+\d{1,2}(\,\s+\d{4})?" + \
                        "\)\s+-\s+(?=[A-Z])", "", text)
        
        # Bracketed lead-ins that work like subtitles excluded from other releases:
        text = re.sub("^\[.*?\]\s+(?=([A-Z]|\"))", "", text)
                
        # look for dateline after header:
        pre = re.search("^.*?([A-Z]*[\s]{0,1}){1,4}\,\s*(VT|VERMONT|Vermont)\s+-\s+(?=[A-Z])", text)
        
        # if that doesn't turn something up, check for DC dateline:
        dc_dateline2 = dc_dateline[:-11] + dc_dateline[-1] # removes all caps search
        if pre == None:
            pre = re.search("^.*?" + dc_dateline2 + "(\s+\(.*?\))?\)?\s+\-\s+(?=[A-Z])", text)
        
        # if still nothing, look for date
        if pre == None:
            pre = re.search("^(Statement|Comment).*?([A-Z]{1}[a-z]{2,}\,\s+)?" + regex_months + \
                            "\s+\d{1,2}(\,\s+\d{4})?" + \
                            "\s+(-\s+)?(\[.*?\]\s+)?(?=(\"|[A-Z]))", text)
        
        # different date style:
        if pre == None:
            pre = re.search("^.*?([A-Z]{1}[a-z]{2,}\,\s+)?" + regex_months + \
                            "\s+\d{1,2}(\,\s+\d{4})?" + \
                            "\)?\s+(-\s+)?(?=[A-Z])", text)
        
        # if any of those finds something, do some diagnostics:
        if pre:
            pre_span = pre.span()
            pre_len = pre_span[1] - pre_span[0]
            pre_frac = pre_len / len(text)
            
            # if 'pre' comprises less than 25% of full text, remove it
            if pre_frac < 0.25:
                text = text[pre_span[1]:]
        
        # Declaring Leahy as speaker:
        text = re.sub("^(Mr\.\s+LEAHY\.|Leahy\:)\s+(?=([A-Z]|\"))", "", text)
        
        
        # look for the text at the end using the octothorpe/pound sign
        post = re.search("-?(#[\s]{0,1}){3,}.*?$", text)
        
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
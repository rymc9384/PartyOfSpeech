# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 13:34:12 2017

@author: Ryan McMahon
"""

#utils

class text_cleaning:
    
    regex_months = "(January|February|March|April|May|June|July|August|" + \
                   "September|October|November|December|Jan\.?|Feb\.?|"  + \
                   "Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Sep\.?|Sept\.?|"  + \
                   "Oct\.?|Nov\.?|Dec\.?)"
    
    dc_dateline = "(WASHINGTON\s?\,? D\.C\s?\.|WASHINGTON\, D\. C\.|"          + \
                  "WASHINGTON\, D\.C|WASHINGTON\, DC|WASHINGTON DC|"    + \
                  "WASHINGTON|WASHINGTON\.|Washington\,\s?D\.C\.|"        + \
                  "Washington D\.C\.|Washington\, D\.C|"                + \
                  "Washington\, D\. C\.|Washington\,? DC|"              + \
                  "Washington|[A-Z]{4,})"
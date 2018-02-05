## Author: Ryan McMahon
## Date Created: 02/05/2018
## Date Last Modified: 02/05/2018
## File: "~/07-descriptive/documents/01-summary_stats.R"

## Purpose: Provide basic descriptives about the corpus, specifically documents 
##          from the 114th Congress.
##      
##

## Edits:
##       
##      
##        

## Notes:
##      
##  

## Local Software Information:
## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

################################################################################


rm(list=ls())
options(stringsAsFactors = F)
library(zoo)


##############################
### 1) LOAD DATA
##############################

# Load functions:
source("D:/Dropbox/Dissertation/02-pos_senate/01-code/PartyOfSpeech/06-robustness/utils_fw.R")

# Read in 114th Congress data:
df <- read.csv("D:/cong_text/csvs/tokenized/topicmodeling/ExpAgendas/topictext_114Cong.csv")


##############################
### 2) FORMAT DATA
##############################

# Format dates:
df$form_date <- as.Date(x = df$form_date, format = "%Y-%m-%d")
df$yearmon <- as.yearmon(x = df$form_date)
df$wkyr <- format(x = df$form_date, format = "%Y-%U")
df$year <- as.integer(format(x = df$form_date, "%Y"))
df$month <- as.integer(format(x = df$form_date, "%m"))
df$day <- as.integer(format(x = df$form_date, "%d"))

# Count tokens:
df$ntokens <- NA

for (i in 1:nrow(df)){
  
  df$ntokens[i] <- count_tokens(df$topic_text[i])

}

# Subset to releases w/ greater than 25 tokens:
df <- df[df$ntokens >= 25, ]


##############################
### 3) SUMMARIES
##############################

## 3.1) Number of docs:
nrow(df)
# 48528


## 3.2) Docs by year:
table(df$year)
# 2015: 28009; 2016: 20519


## 3.3) Docs by Senator:
( sen.tab <- table(df$sen) )
mean(sen.tab)
# 485.28
range(sen.tab)
# 97, 1919; billnelson and brown, respectively
median(sen.tab)
# 427.5


## 3.4) Docs by Senator-year:
senyr.tab <- table(df$year, df$sen)
mean(senyr.tab)
# 242.64
median(senyr.tab)
# 213


## 3.5) Docs by day:
day.tab <- table(df$form_date)
mean(day.tab)
# 72.64671
median(day.tab)
# 66


## 3.6) Docs by day (including days w/ 0):
fulldates <- length(min(df$form_date):max(df$form_date))
# 675

day2.tab <- day.tab
day2.tab[(length(day2.tab) + 1):fulldates] <- 0
mean(day2.tab)
# 71.8933
median(day2.tab)
# 65
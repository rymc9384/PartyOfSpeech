## Author: Ryan McMahon
## Date Created: 11/29/2017
## Date Last Modified: 11/29/2017
## File: "~/06-robustness/02-noun_ratios/01-just_nouns.R"

## Purpose: 
##      
##

## Edits:
##      
##        

## Notes:
##      11/29/17) Based on "../../05-analysis/02-noun_ratios.R"
##  

## Local Software Information:
## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

################################################################################

rm(list=ls())
library(stringr)
library(optparse)
options(stringsAsFactors = F)

## Parse command line arguments:
option_list <- list(
  make_option(c("-i", "--infile"), type="character", default="D:/cong_text/final_pos/topic_lemtag_merged_114.csv", 
              help="Merged topic lemma file [default=%default]", metavar="character"),
  make_option(c("-lf", "--logfile"), type="character", default="./just_nouns.Rout", 
              help="logfile name [default= %default]", metavar="character")
) 

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)


sink(file = opt$logfile)
## Display package versions and other environment information:
cat("\tSession info:\n")
sessionInfo()

#########################
### 0) DEFINE FUNCTIONS
#########################


get_tags <- function(text){
  
  grams <- unlist(str_split(text, ' '))
  grams <- gsub(pattern = ".*_", replacement = '', grams)
  
  return(grams)
  
}

noun_ratio <- function(grams){
  
  
  n.count <- str_count(string = grams, pattern = "NNS?(?=$)")
  n.ratio <- sum(n.count) / length(grams)
  
  return(n.ratio)
  
}


#########################
### 1) READ IN DATA
#########################
cat(paste0("\nReading in ", opt$infile, "...\n"))
merged <- read.csv(opt$infile)


#########################
### 2) COUNT NOUNS
#########################

cat("Counting nouns...\n")

merged$nouns <- NA

for (i in 1:nrow(merged)){
  
  grams <- get_tags(text = merged$lemma_text[i])
  merged$nouns[i] <- noun_ratio(grams = grams)
  
}


#########################
### 3) T-TESTS
#########################

cat(paste0(rep("*", 15)))
cat("\t\tPERFORMING T-TESTS\t\t")
cat(paste0(rep("*", 15)))

r.nn <- merged$nouns[merged$party=="R"]
d.nn <- merged$nouns[merged$party != "R"]


# 3.1) Null = 0:
nn0.ttest <- t.test(x = r.nn, y = d.nn, mu = 0.00, var.equal = FALSE)


# 3.2) Null = 0.01:
nn1.ttest <- t.test(x = r.nn, y = d.nn, mu = 0.01, var.equal = FALSE)


# 3.3) Printing:
cat("\n\nNull = 0 t-test:")
print(nn0.ttest)

cat("\n\nNull = 0.01 t-test:")
print(nn1.ttest)


## Stop logging:
cat("\n\n\tDONE!!")
sink()


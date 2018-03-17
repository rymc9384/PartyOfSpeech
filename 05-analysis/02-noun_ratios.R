## Author: Ryan McMahon
## Date Created: 11/09/2017
## Date Last Modified: 03/12/2018
## File: "~/05-analysis/02-noun_ratios.R"

## Purpose: 
##      
##

## Edits:
##      11/26/17) Save t-test results as RData file, in addition to log file.
##      03/12/18) Drop releases w/ fewer than 25 tokens.
##        
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
  make_option(c("-lf", "--logfile"), type="character", default="./noun_ratios.Rout", 
              help="logfile name [default= %default]", metavar="character"),
  make_option(c("-o", "--outfile"), type="character", default="D:/cong_text/final_pos/analysis/noun_ratios.RData", 
              help="ttest out file w/ path [default= %default]", metavar="character")
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

noun_ratio <- function(grams, propernouns=FALSE){
  
  if (propernouns){
    n.count <- str_count(string = grams, pattern = "(NN.*|PRP[$]?)")
  } else{
    n.count <- str_count(string = grams, pattern = "(NNS?|PRP[$]?)(?=$)")
  }
  
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

merged$ntoks <- NA
merged$allnouns <- NA
merged$nopropnouns <- NA

for (i in 1:nrow(merged)){
  
  grams <- get_tags(text = merged$lemma_text[i])
  
  merged$ntoks[i] <- length(grams)
  merged$allnouns[i] <- noun_ratio(grams = grams, propernouns = TRUE)
  merged$nopropnouns[i] <- noun_ratio(grams = grams, propernouns = FALSE)
  
}


## Drop releases with fewer than 25 tokens:
merged <- merged[merged$ntoks >= 25, ]


#########################
### 3) T-TESTS
#########################

cat(paste0(rep("*", 15)))
cat("\t\tPERFORMING T-TESTS\t\t")
cat(paste0(rep("*", 15)))

# 3.1) All nouns:
r.allnn <- merged$allnouns[merged$party=="R"]
d.allnn <- merged$allnouns[merged$party != "R"]
allnn.ttest <- t.test(x = r.allnn, y = d.allnn, mu = 0.01, var.equal = FALSE)

# 3.2) No proper nouns:
r.noprop <- merged$nopropnouns[merged$party=="R"]
d.noprop <- merged$nopropnouns[merged$party != "R"]
noprop.ttest <- t.test(x = r.noprop, y = d.noprop, mu = 0.01, var.equal = FALSE)

cat("\n\nAll nouns t-test:")
print(allnn.ttest)

cat("\n\nNo proper nouns t-test:")
print(noprop.ttest)


# 3.3) Saving:
cat("\n\nSaving t-test results...\n")
save(allnn.ttest, noprop.ttest, file = opt$outfile)


## Stop logging:
cat("\n\n\tDONE!!")
sink()


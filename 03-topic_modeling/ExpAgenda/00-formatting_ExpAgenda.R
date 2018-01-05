## Author: RBM
## Date Created: 10/04/2017
## Date Last Modified: 10/18/2017
## File: "~/03-topic_modeling/ExpAgenda/00-formatting_ExpAgenda.R"
##
## PURPOSE: This formats the tokenized text output for use in the ExpAgenda 
##          model using a modified version of Grimmer's (2010) preprocessing 
##          code.
##
## NOTES: 
##        
##
## EDITS:
##       10/18/17) Remove numbers - limits vocab size, fewer params to estimate.
##        
##

## Software Information:

## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

## "tm" package: 0.7-1 (depends on "NLP" package: 0.1-10)
## "SnowballC" package: 0.5.1
## "optparse" package: 1.4.4 (depends on "getopt" package: 1.20.0)

################################################################################


rm(list=ls())
library(tm)
library(optparse)
options(stringsAsFactors = F)

## Parse command line arguments:
option_list <- list(
  make_option(c("-i", "--infile"), type="character", default="D:/cong_text/csvs/tokenized/topicmodeling/ExpAgendas/topictext_114Cong.csv", 
              help="Tokenized and processed text infile path [default=%default]", metavar="character"),
  make_option(c("-op", "--outpath"), type="character", default="./Processed/", 
              help="output directory [default= %default]", metavar="character"),
  make_option(c("-to", "--textoutfile"), type="character", default="ExpAgenda_TextDF_114.RData", 
              help="textoutput file name [default= %default]", metavar="character"),
  make_option(c("-po", "--processedoutfile"), type="character", default="ExpAgenda_Processed_114.RData", 
              help="processed output file name [default= %default]", metavar="character")
  ) 

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)


## Set working directory and executing modified processing script:
setwd("D:/Dropbox/Dissertation/02-pos_senate/01-code/03-topic_modeling/ExpAgenda")
source(file = "./ExpAgenda-master/R/PreProcess.R")


## Read in tokenized text data:
textsDF <- read.csv(file = opt$infile)


## Get rid of documents that are less than 25 tokens long:

# Get document lengths
textlens <- NA
for (i in 1:length(textsDF$topic_text)){
  
  temptext <- textsDF$topic_text[i]
  temptext <- unlist(strsplit(x = temptext, split = " "))
  textlens[i] <- length(temptext)
  
}

# Filter by doc length:
textsDF <- textsDF[which(textlens >= 25), ]


## Get rid of authors with only 1 document:

# Get number of docs per author:
numdocs <- unlist(by(data = textsDF,INDICES = textsDF$sen, FUN = nrow))

# Filter authors:
bad.authors <- names(which(numdocs == 1))
textsDF <- textsDF[which(textsDF$sen %in% bad.authors == F),]


## Number rows and process text:

textsDF$docnum <- 1:nrow(textsDF)

processed <- PreProcess(textsDF = textsDF, TextsCol = "topic_text", 
                      AuthorCol = "sen", IDCol = "docid", 
                      StopWords = NULL, removeNumbers = TRUE)

if (!dir.exists(opt$outpath)){
  dir.create(path = opt$outpath, recursive = TRUE)
}

setwd(opt$outpath)

save(textsDF, file = opt$textoutfile)
save(processed, file = opt$processedoutfile)

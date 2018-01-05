## Author: RBM
## Date Created: 10/11/2017
## Date Last Modified: 10/12/2017
## File: "~/03-topic_modeling/ExpAgenda/04-select_num_topics.R"
##
## PURPOSE: This 
##
## NOTES: 
##        
##
## EDITS:
##       10/12/17) Add description of arguments for `high_docs()` function.
##        
##

## Software Information:

## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

## "DataCombine" package: 0.2.21 (depends on "data.table" package: 1.10.4)
## "optparse" package: 1.4.4 (depends on "getopt" package: 1.20.0)

################################################################################


rm(list=ls())
library(DataCombine)
library(optparse)

options(stringsAsFactors = F)
set.seed(11932)

## Parse command line arguments:
option_list <- list(
  make_option(c("--topsumscript"), type="character", default="D:/Dropbox/Dissertation/02-pos_senate/01-code/03-topic_modeling/ExpAgenda/ExpAgenda-master/R/TopicSummary.R", 
              help="path to topic summary script from grimmer [default= %default]", metavar="character"),
  make_option(c("--fitspath"), type="character", default="D:/cong_text/rdata/topic_modeling/model_fits/Fits/114/", 
              help="path to topic model fits [default= %default]", metavar="character"),
  make_option(c("--outpath"), type="character", default="D:/Dropbox/Dissertation/02-pos_senate/01-code/03-topic_modeling/ExpAgenda/num_topics/", 
              help="path to where sink file will be saved [default= %default]", metavar="character"),
  make_option(c("--outfile"), type="character", default="select_num_topics_114.Rout", 
              help="logging/sink file name [default= %default]", metavar="character")
) 

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)


#############################################
### 0) SET UP ENVIRONMENT
#############################################

## 0.a) Open outfile:
if (!dir.exists(opt$outpath)){
  dir.create(path = opt$outpath, recursive = TRUE)
}

outfile.sink <- paste0(opt$outpath, opt$outfile)

sink(file = outfile.sink)


## 0.b) Execute the topic summary script from Grimmer (2010):
source(opt$topsumscript)


## 0.c) Find model fits:
fits <- list.files(path = opt$fitspath, full.names = T)


## 0.e) Printing functions:

# 0.e.1) print model fit header:
print_header <- function(ntops){
  ##################
  ## ARGS:
  # 1) ntops (integer) = Number of topics fit by model
  #
  ##################
  
  stars <- paste0(rep("*", 70), collapse = "")
  title <- paste0("\t\t\tMODEL WITH ", ntops, " TOPICS\n")
  header <- paste0(stars, "\n", title, stars, "\n\n")
  
  cat(header)
  
}


# 0.e.2) put together the string for a single topic:
paste_topic <- function(x, separator="  "){
  ##################
  ## ARGS:
  # 1) x (dataframe) = Single topic subset from dataframe returned by the 
  #                    `TopicSummary()`` function, with added column for 
  #                     docs w/ highest prob of being in topic
  # 2) separator (character, default="\s\s") = How to separate the stems when printing
  #
  ##################
  
  line1 <- paste0("Topic ", x$TopicNumber[1], ":\n")
  line2 <- paste0("\tHigh Prob Documents: ", x$topdocs[1], "\n")
  line3 <- paste(paste0(x$Stems, " (", x$Mus, ")"), collapse = separator)
  out <- paste0(line1, line2, line3, "\n\n", collapse="")
  
  return(out)
  
}


# 0.e.3) print strings for all topics:
print_topics <- function(x, digits=2, separator="  "){
  ##################
  ## ARGS:
  # 1) x (dataframe) = Object returned by the `TopicSummary()`` function
  # 2) digits (integer; default=2) = Number of decimals to round the Mus 
  # 3) separator (character, default="\s\s") = How to separate the stems when printing
  #
  ##################
  
  
  
  # Round the Mus:
  x$Mus <- round(x$Mus, digits)
  
  outs <- by(data = x, INDICES = x$TopicNumber, FUN = paste_topic, separator)
  
  cat(outs)
  
}


# 0.e.4) get 5 random docs w/ high prob of being in topic:
high_docs <- function(x){
  ##################
  ## ARGS:
  # 1) x (vector, D x 1) = column vector of pr(D_i) comes from topic k
  #
  ##################
  
  high_probs <- which(x > 0.99)
  high_probs <- sample(high_probs, size = 5, replace = F)
  out <- paste(high_probs, collapse = ", ")
  
}


#############################################
### 1) PRINT TOP WORDS BY TOPIC
#############################################

n <- 10

for ( fit in fits ){
  
  
  # load model fit
  load(fit)
  
  # get top words for each topic by mutual information
  topSum <- TopicSummary(obj = expAgenda, NStems = n)
  
  # get number of topics
  ntops <- nrow(topSum) / 10
  
  # get top 5 documents for each topic from expAgenda `rs` params
  topdocs <- apply(expAgenda$rs, 2, high_docs)
  
  # format to merge with `topSum` object:
  topdocs <- data.frame(list("id"=1:ntops, "topdocs"=topdocs))
  topdocs <- do.call("rbind", replicate(n, topdocs, simplify = FALSE))
  topdocs <- topdocs[order(topdocs$id), ]
  
  # put the top docs strings into the `topSum` object
  topSum$topdocs <- topdocs$topdocs
  
  # print fit header information
  cat("\n\n")
  print_header(ntops)
  
  # print formatted topics' top words
  print_topics(x = topSum, digits = 2, separator = "  ")
  cat("\n\n")
  
  # remove fit object
  rm(expAgenda)
  
}


sink()

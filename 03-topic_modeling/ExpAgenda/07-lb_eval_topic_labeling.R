## Author: RBM
## Date Created: 10/17/2017
## Date Last Modified: 10/17/2017
## File: "~/03-topic_modeling/ExpAgenda/07-lb_eval_topic_labeling.R"
##
## PURPOSE: This code evaluates the lower-bounds for the replication fits.
##          Then, using the selected replication model, summarizes topics 
##          via a "top-n" words by mutual information. Finally, documents 
##          are sampled from each topic for reading and topic labeling. 
##          
##
## NOTES: 
## 
##
## EDITS:
##        
##

## Software Information:

## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

## "DataCombine" package: 0.2.21 (depends on "data.table" package: 1.10.4)
## "optparse" package: 1.4.4 (depends on "getopt" package: 1.20.0)

################################################################################


rm(list = ls())
library(DataCombine)
library(optparse)
options(stringsAsFactors = FALSE)

set.seed(11769)

## Parse command line arguments:
option_list <- list(
  make_option(c("--topsumscript"), type="character", default="./ExpAgenda-master/R/TopicSummary.R", 
              help="expressed agenda topic summary script [default= %default]", metavar="character"),
  make_option(c("-b", "--bounds"), type="character", default="./num_topics/lower_bounds_114.RData", 
              help="lower bounds rdata file [default= %default]", metavar="character"),
  make_option(c("--textdfin"), type="character", default="./Processed/ExpAgenda_TextDF_114.RData", 
              help="cleaned texts dataframe rdata file [default= %default]", metavar="character"),
  make_option(c("--tdfoutpath"), type="character", default="D:/cong_text/csvs/topics/", 
              help="path to textsDF w/ topic numbers will be stored [default= %default]", metavar="character"),
  make_option(c("--tdfoutfile"), type="character", default="ExpAgenda_Topics_114.csv", 
              help="filename of textsDF w/ topic numbers [default= %default]", metavar="character"),
  make_option(c("--toplabelpath"), type="character", default="./topic_labeling/", 
              help="log file name [default= %default]", metavar="character"),
  make_option(c("--toplabelfile"), type="character", default="topic_labeling_114.csv", 
              help="log file name [default= %default]", metavar="character")
) 

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)


#############################################
### 0) SET UP ENVIRONMENT
#############################################

message("Setting up the environment...")

## 0.a) Execute the topic summary script from Grimmer (2010):
source(opt$topsumscript)


## 0.b) Load text data (textsDF):
load(opt$textdfin)


## 0.v) Load lower-bounds data (run_summary):
load(opt$bounds)



#############################################
### 1) FUNCTIONS
#############################################

message("Defining functions...")


## 1.a) Index of Maximum:
w_max <- function( x ){
  
  ##################
  ## ARGS:
  # 1) x (vector) = vector of sortable values
  #
  ##################
  
  return( which(x == max(x)) )
  
}


## 1.b) Get topic assignments:
max_topic <- function( topics ){
  
  ##################
  ## ARGS:
  # 1) topics (matrix, D x K) = matrix of topic probabilities
  # 
  #
  ##################
  
  max_t <- apply(X = topics, MARGIN = 1, FUN = w_max)
  
  return(max_t)
  
}



## 1.c) Document Sampling Function:
samp_docs <- function( file_topic_df, n_docs = 10 ){
  # @param file_topic_df: df, 1st column holds document file names (str) 
  #                                  and 2nd holds their topic assignment (int)
  # @param n_docs: integer, how many documents to sample from each topic 
  #                         (defaults to 10)
  # 
  # Returns data frame of sampled filenames and their assigned topics.
  
  n_topics <- length(unique(file_topic_df[,2]))
  
  sampled_docs <- list()
  
  for (t in 1:n_topics){
    
    top_docs <- file_topic_df[which(file_topic_df[,2] == t), ]
    samp <- sample(x = 1:nrow(top_docs), size = n_docs, replace = F)
    sampled_docs[[t]] <- top_docs[samp,]
    
  }
  
  sampled_docs <- do.call(what = rbind, args = sampled_docs)
  
  return(sampled_docs)
  
}



#############################################
### 2) EVALUATE BOUNDS
#############################################

message("Selecting best run and loading fit...")


## 2.a) Which run has max lower-bound:
best.run <- w_max(run_summary$lower.bound)


## 2.b) Load that run (expAgenda):
load(run_summary$file[best.run]) 



#############################################
### 3) TOPIC KEYWORDS
#############################################

message("Getting top stems by MI...")


## 3.a) Get top 10 words by MI:
top_sum <- TopicSummary(obj = expAgenda, NStems = 10)



#############################################
### 4) TOPIC ASSIGNMENT
#############################################


message("Assigning documents to topics...")

## 4.a) Get max topic probs by doc:
max.topic <- max_topic(topics = expAgenda$rs)


## 4.b) Put into textsDF:
textsDF$topic <- max.topic


## 4.c) Subset "topic_text" out of `textsDF`:
textsDF <- textsDF[, colnames(textsDF) != "topic_text" ]


#############################################
### 5) DOCUMENT SAMPLING
#############################################

message("Sampling documents for labeling...")


## 5.a) Format data for document sampling:
file_topic_df <- textsDF[,c( "docid", "topic" ) ]


## 5.b) Sample documents:
sampled_docs <- samp_docs(file_topic_df = file_topic_df, n_docs = 10)



#############################################
### 6) FORMAT LABELING INFO
#############################################

message("Formatting labeling data...")


## 6.a) Generate strings from top stems:
top.stem.strings <- unlist( by(data = top_sum$Stems, top_sum$TopicNumber, paste, collapse = ", ") )


## 6.b) Generate strings from sampled document IDs:
top.docid.strings <- unlist( by(data = sampled_docs$docid, sampled_docs$topic, paste, collapse = ", ") )


## 6.c) Make topic labeling dataframe:
top.labeling.out <- data.frame( list( "topic" = 1:length(top.stem.strings),
                                      "stems" = as.vector( top.stem.strings ),
                                      "docs" = as.vector( top.docid.strings ) 
                                      ) )


#############################################
### 7) SAVING
#############################################

message("Saving document and topic labeling data...")

## 7.a) Path creation:
if (!dir.exists(opt$tdfoutpath)){
  dir.create(path = opt$tdfoutpath, recursive = TRUE)
}

if (!dir.exists(opt$toplabelpath)){
  dir.create(path = opt$toplabelpath, recursive = TRUE)
}


## 7.b) File naming:
tdf.outfile <- paste0(opt$tdfoutpath, opt$tdfoutfile)
toplabel.outfile <- paste0(opt$toplabelpath, opt$toplabelfile)


## 7.c) Save output:
write.csv(x = textsDF, file = tdf.outfile, row.names = F, fileEncoding = "utf-8")
write.csv(x = top.labeling.out, file = toplabel.outfile, row.names = F, fileEncoding = "utf-8")


message("DONE!")
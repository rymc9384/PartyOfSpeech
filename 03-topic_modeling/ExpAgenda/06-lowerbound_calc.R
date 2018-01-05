## Author: RBM
## Date Created: 10/13/2017
## Date Last Modified: 10/25/2017
## File: "~/03-topic_modeling/ExpAgenda/06-lowerbound_calc.R"
##
## PURPOSE: This code calculates the lowerbound for KL-Divergence in Grimmer's 
##          Expressed Agenda model (2010) over the replication runs. 
##          The math comes from the Technical Notes, equation 1.6 (pg. 5) and 
##          the main text.
##
## NOTES: 
##        10/13/17) The lower-bounds calculated here are greater than 0. This 
##                  is because a normalizing constant (for the $\kappa$ vector), 
##                  which transforms the vMF into a proper PDF,
##                  is dropped from the equation. It is dropped b/c the model 
##                  doesn't estimate kappa, instead leaving it as a predefined 
##					scalar, and calculating the constant is computationally 
##					expensive. The full formula has the additonal term of:
##                  + log( C_p( \kappa ) )
##
##                  Because C_p( \kappa ) is very small, its log would force 
##                  the lower-bound less than 0. 
##                  See: https://en.wikipedia.org/wiki/Von_Mises%E2%80%93Fisher_distribution
## 
##
## EDITS:
##        10/16/17) Edit default `--reppath` option; Add in note about section headers.
##        10/25/17) Add in some Sys.output so user isn't totally in the dark about what; 
##                  fix indexing for thetas in author loop - line 475 
##

## Software Information:

## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

## "optparse" package: 1.4.4 (depends on "getopt" package: 1.20.0)

################################################################################


rm(list = ls())
library(optparse)
options(stringsAsFactors = FALSE)


## Parse command line arguments:
option_list <- list(
  make_option(c("--reppath"), type="character", default="D:/cong_text/rdata/topic_modeling/rep_fits/Replications/114/", 
              help="path to replication runs [default= %default]", metavar="character"),
  make_option(c("-p", "--processed"), type="character", default="./Processed/ExpAgenda_Processed_114.RData", 
              help="processed text rdata file [default= %default]", metavar="character"),
  make_option(c("--outpath"), type="character", default="./num_topics/", 
              help="path to where lower-bounds will be stored [default= %default]", metavar="character"),
  make_option(c("--outfile"), type="character", default="lower_bounds_114.RData", 
              help="output file name [default= %default]", metavar="character")
) 

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)


#############################################
### 0) SET UP ENVIRONMENT
#############################################

## 0.a) Read in processed text data:
load(opt$processed)

## 0.b) Extract TDM and throw out other processed data:
ys <- processed$term.doc
rm(processed)

## 0.c) Get file names for  the replication runs:
infiles <- list.files(path = opt$reppath, pattern = "*.RData", full.names = T)


########## Functions for calculating lower-bound ##########

# Note "LINE [#]" refers to line in eq. 1.6, pg 5 of technical notes 
# from Grimmer (2010).

#############################################
### 1) LINE 1 FUNCTIONS
#############################################


## 1.a) Prob doc is from topic k, times kappa, times (word params * normalized doc):
line1.rkappamuystar <- function(docs.i, ys.i, thetas.i, mus, rs.i, kappa){
  
  ##################
  ## ARGS:
  # 1) docs.i (vector, 1 x D) = Index of documents associated with the author 
  # 2) ys.i (matrix, D_i x |V|) = TDM, subset to author's docs
  # 3) thetas.i (vector, 1 x K) = Expected number of docs the author writes in topic k, k\in{1:K},
  #                             plus some extra ~50 docs or so (determined by the sum of alpha)
  # 4) mus (matrix, |V| x K) = Location on the unit hyperspace where the vMF distribution reaches 
  #                            its mode for each stem w, w\in{1:|V|}
  # 5) rs.i (matrix, D_i x K) = Probability document j, j\in{1:D_i}, belongs to topic k, k\in{1:K}
  # 6) kappa (scalar) = dispersion parameter on vMF distribution used for model fitting.
  #
  ##################
  
  out <- 0
  
  # loop over author docs:
  for ( j in seq_along(docs.i) ){
    
    # the norm for docs.i[j]
    y.len <- c(ys.i[j,] %*%  ys.i[j,])
    
    if ( y.len == 0 ){
      next
    }
    
    # ystar from paper (i.e., word counts / doc norm)
    y.star <- ys.i[j,] / y.len
    
    
    # loop over topics:
    for ( k in seq_along(thetas.i) ){
      
      out <- out + c( rs.i[j, k] * kappa * t(mus[,k]) %*% y.star )
    }
    
  }
  
  return(out)
  
}



## 1.b) Prob doc is from topic k, times (digamma theta_k - digamma sum(theta)):
line1.rdigammadiff <- function(docs.i, thetas.i, rs.i){
  
  ##################
  ## ARGS:
  # 1) docs.i (vector, 1 x D) = Index of documents associated with the author 
  # 2) thetas.i (vector, 1 x K) = Expected number of docs the author writes in topic k, k\in{1:K},
  #                             plus some extra ~50 docs or so (determined by the sum of alpha)
  # 3) rs.i (matrix, D_i x K) = Probability document j, j\in{1:D_i}, belongs to topic k, k\in{1:K}
  #
  ##################
  
  out <- 0
  
  # sum across all thetas.i:
  thetas.i.sum <- sum(thetas.i)
  
  # loop over author docs:
  for ( j in seq_along(docs.i) ){
    
    # loop over topics:
    for (k in seq_along(thetas.i)){
      
      digamdiff <- digamma(x = thetas.i[k]) - digamma(thetas.i.sum)
      out <- out + (rs.i[j,k] * digamdiff)
      
    }
    
  }
  
  return(out)
  
}



## 1.c) log gamma difference in prior sums:
line1.loggammaalphadiff <- function(alpha){
  
  ##################
  ## ARGS:
  # 1) alpha (vector, 1 x K) = Prior on number of docs in each topic for an author, uniform across all authors.
  #
  ##################
  
  lg.alphasum <- lgamma(x = sum(alpha))
  sum.lgalpha <- sum(lgamma(x = alpha))
  
  return(lg.alphasum - sum.lgalpha)
  
}




#############################################
### 2) LINE 2 FUNCTIONS
#############################################


## 2.a) priors minus 1, times difference in sums of digamma expected docs:
line2.alphamin1digammadiff <- function(alpha, thetas.i){
  
  ##################
  ## ARGS:
  # 1) alpha (vector, 1 x K) = Prior on number of docs in each topic for an author, uniform across all authors.
  # 2) thetas.i (vector, 1 x K) = Expected number of docs the author writes in topic k, k\in{1:K},
  #                             plus some extra ~50 docs or so (determined by the sum of alpha)
  #
  ##################
  
  # sum across all thetas.i:
  thetas.i.sum <- sum(thetas.i)
  
  # alphas minus 1:
  alphamin1 <- alpha - 1
  
  # digamma diffs:
  digammadiffs <- (digamma(thetas.i) - digamma(thetas.i.sum))
  
  # multiplying and summing:
  out <- c(alphamin1 %*% digammadiffs)
  
  return(out)
  
}



## 2.b) log gamma sum(thetas) plus sum( log gamma thetas ):
line2.loggsumtheta.sumloggtheta <- function(thetas.i){
  
  ##################
  ## ARGS:
  # 1) thetas.i (vector, 1 x K) = Expected number of docs the author writes in topic k, k\in{1:K},
  #                             plus some extra ~50 docs or so (determined by the sum of alpha)
  #
  ##################
  
  # sum across all thetas.i:
  thetas.i.sum <- sum(thetas.i)
  
  # log gamma sum( thetas ):
  loggsumtheta <- lgamma(x = thetas.i.sum)
  
  # sum ( log gamma thetas )
  sumloggtheta <- sum(lgamma(x = thetas.i))
  
  # together (w/ minus sign incorporated):
  out <-  (-1 * loggsumtheta) + sumloggtheta
  
  return(out)
  
}




#############################################
### 3) LINE 3 FUNCTIONS
#############################################


## 3.a) ( theta minus 1 ) times digamma theta diff:
line3.thetamin1digammadiff <- function(thetas.i){
  
  ##################
  ## ARGS:
  # 1) thetas.i (vector, 1 x K) = Expected number of docs the author writes in topic k, k\in{1:K},
  #                             plus some extra ~50 docs or so (determined by the sum of alpha)
  #
  ##################
  
  # sum across all thetas.i:
  thetas.i.sum <- sum(thetas.i)
  
  # theta minus 1:
  thetasmin1 <- thetas.i - 1
  
  # digamma diffs:
  digammadiffs <- (digamma(thetas.i) - digamma(thetas.i.sum))
  
  # multiplying and summing:
  out <- c(thetasmin1 %*% digammadiffs)  
  
  # incorporate minus sign:
  out <- -1 * out
  
  return(out)
  
}



## 3.b) Prob doc is from topic k, times log prob doc is from topic k:
line3.rlogr <- function(rs.i){
  
  ##################
  ## ARGS:
  # 1) rs.i (matrix, D_i x K) = Probability document j, j\in{1:D_i}, belongs to topic k, k\in{1:K}
  #
  ##################
  
  out <- 0 
  
  # loop over docs.i:
  for (j in 1:nrow(rs.i)){
    
    # loop over topics:
    for (k in 1:ncol(rs.i)){
      
      # skip over zeroes to avoid missing vals:
      if (rs.i[j, k] == 0){
        next
      }
      
      # prob * log prob
      out <- out + (rs.i[j,k] * log(rs.i[j,k]))
      
    }
    
  }
  
  # incorporate minus sign:
  out <- -1 * out
  
  return(out)
  
}



# 3.c) prior dispersion, times prior center, times word locations for topic:
line3.kappaetamu <- function(kappa, eta, mus){
  
  ##################
  ## ARGS:
  # 1) kappa (scalar) = dispersion parameter on vMF distribution used for model fitting.
  # 2) eta (vector, 1 x |V|) = Center of prior vMF distribution
  # 3) mus (matrix, |V| x K) = Location on the unit hyperspace where the vMF distribution reaches 
  #                            its mode for each stem w, w\in{1:|V|}
  #
  ##################
  
  out <- 0
  
  # loop over topics:
  for (k in 1:ncol(mus)){
    
    # dot product eta-transpose mus_k:
    etat.mu <- c( t(eta) %*% mus[,k] )
    
    # pre multiply by kappa scalar:
    kappa.etat.mu <- kappa * etat.mu
    
    out <- out + kappa.etat.mu
    
  }
  
  return(out)
  
}



# 3.d) sum negative alpha:
line3.sumnegalpha <- function(alpha){
  
  ##################
  ## ARGS:
  # 1) alpha (vector, 1 x K) = Prior on number of docs in each topic for an author, uniform across all authors.
  #
  ##################
  
  out <- sum(-1 * alpha)
  
  return(out)
  
}


#############################################
### 4) COMBINED FUNCTION
#############################################


author_bound <- function(docs.i, ys.i, thetas.i, mus, rs.i, alpha, kappa, eta){
  
  ##################
  ## ARGS:
  # 1) docs.i (vector, 1 x D) = Index of documents associated with the author 
  # 2) ys.i (matrix, D_i x |V|) = TDM, subset to author's docs
  # 3) thetas.i (vector, 1 x K) = Expected number of docs the author writes in topic k, k\in{1:K},
  #                             plus some extra ~50 docs or so (determined by the sum of alpha)
  # 4) mus (matrix, |V| x K) = Location on the unit hyperspace where the vMF distribution reaches 
  #                            its mode for each stem w, w\in{1:|V|}
  # 5) rs.i (matrix, D_i x K) = Probability document j, j\in{1:D_i}, belongs to topic k, k\in{1:K}
  # 6) alpha (vector, 1 x K) = Prior on number of docs in each topic for an author, uniform across all authors.
  # 7) kappa (scalar) = dispersion parameter on vMF distribution used for model fitting
  # 8) eta (vector, 1 x |V|) = Center of prior vMF distribution
  #
  ##################
  
  out <- 0
  
  # line 1 calculations:
  out <- out + line1.rkappamuystar(docs.i, ys.i, thetas.i, mus, rs.i, kappa)
  out <- out + line1.rdigammadiff(docs.i, thetas.i, rs.i)
  out <- out + line1.loggammaalphadiff(alpha)
  
  
  # line 2 calculations:
  out <- out + line2.alphamin1digammadiff(alpha, thetas.i)
  out <- out + line2.loggsumtheta.sumloggtheta(thetas.i)
  
  
  # line 3 calculations:
  out <- out + line3.thetamin1digammadiff(thetas.i)
  out <- out + line3.rlogr(rs.i)
  out <- out + line3.kappaetamu(kappa, eta, mus)
  out <- out + line3.sumnegalpha(alpha)
  
  
  # return
  return(out)
  
}



#############################################
### 5) APPLYING OVER RUNS
#############################################

# list to hold outputs:
runs <- list()

# replication numbers as names:
reps <- gsub( pattern = ".*_(?=[0-9]{1,3}_45)", replacement = "", x = infiles, perl=T )
reps <- as.integer( gsub("_45.*$", "", reps) )

# sort infiles by run number:
infiles <- infiles[order(reps)]

# loop over replications in order of run number:
for ( i in seq_along(infiles) ){
	
  cat("Loading file ", i, "\n")
  
  # load model fit
  load(file = infiles[i])
  
  # get author names and vector marking the documents:
  authors <- unique(expAgenda$authorID$sen)
  authorID <- expAgenda$authorID
  
  # extract the model parameters:
  thetas <- expAgenda$thetas
  mus <- expAgenda$mus
  rs <- expAgenda$rs
  alpha <- expAgenda$alpha
  kappa <- 100
  eta <- rep(x = 1/sqrt(ncol(ys)), ncol(ys))
  
  
  # vector to hold results from each senator:
  lq <- NA
  
  # number of authors:
  n_authors <- length(authors)
  
  cat("Calculating lower-bound...\n")
  
  # loop over senators:
  for (j in seq_along(authors)){
    
	cat("\t", j, "/", n_authors, "\n")
	
    docs.i <- authorID$ID[which(authorID$sen == authors[j])]
    ys.i <- ys[docs.i, ]
    thetas.i <- thetas[j, ]
    rs.i <- rs[docs.i, ]
    
    lq[j] <- author_bound(docs.i, ys.i, thetas.i, mus, rs.i, alpha, kappa, eta)
    
  }
  
  names(lq) <- authors
  
  runs[[i]] <- lq
  
  
}


## Get sum over authors for each run (i.e., lower-bound):
run_sums <- unlist(lapply(runs, sum))
run_summary <- data.frame(list("file"=infiles, "lower.bound"=run_sums))


## Save the vectors and sums:
setwd(opt$outpath)
save(runs, run_summary, file = opt$outfile)

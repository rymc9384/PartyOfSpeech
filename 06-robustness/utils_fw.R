## Author: Ryan McMahon
## Date Created: 12/07/2017
## Date Last Modified: 03/27/2018
## File: "~/06-robustness/utils_fw.R"

## Purpose: 
##      
##

## Edits:
##      03/27/18) Add plotting func w/o labeled points
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

rm(list = ls())
library(stringr)
options(stringsAsFactors = F)


###
count_tokens <- function(text){
  
  tokes <- unlist(strsplit(x = text, split = ' '))
  return(length(tokes))
  
}


###
make_counts <- function(x, count_cols, party=c('R','D'), topic=0, totalcol='words', 
                        outcolnames=c('word','counts1', 'priors1')){
  #############
  # x (dataframe) = data frame containing counts by doc and identifying info;
  #                 needs column named 'party' with repubs identified using 'R';
  #                 needs column named 'topic' w/ integer values
  # count_cols (str) = column name with counts from `str_extract_all()`
  # party (str) = 'R' or 'D'
  # topic (int) = 0 for all topics or positive val identifying topic to use
  # totalcol (str) = column name containing total word counts for document
  # outcolnames vec(str,str) = vector of 3 strings that will be column names of output
  ################
  
  avg_doclen <- mean(x[,totalcol])
  
  tmp_x <- x
  outcounts <- list()
  
  
  if (party == 'R'){
    x <- x[which(x$party == 'R'), ]
  } else{
    x <- x[which(x$party != 'R'), ]
  }
  
  
  if (topic > 0){
    
    x <- x[which(x$topic == topic), ]
    tmp_x <- tmp_x[which(tmp_x$topic != topic), ]
    
    # loop over features:
    for (i in 1:length(count_cols)){
      # counts in relevant topic
      tmp_table1 <- table(unlist(x[,count_cols[i]]))
      tmp_table1 <- data.frame(tmp_table1)
      colnames(tmp_table1) <- outcolnames[1:2]
      tmp_table1[,1] <- as.character(tmp_table1[,1])
      
      # priors
      tmp_table2 <- table(unlist(tmp_x[, count_cols[i]]))
      tmp_table2 <- data.frame(tmp_table2)
      colnames(tmp_table2) <- outcolnames[c(1,3)]
      tmp_table2[,1] <- as.character(tmp_table2[,1])
      
      
      a0 <- avg_doclen * nrow(x)
      # need to scale by all words, not just ones we're interested in;
      # thus using the total col and not sum of priors (like in python scripts, which use full DTM)
      tmp_table2[,2] <- tmp_table2[,2] * (a0/sum(tmp_x[,totalcol])) 
      
      
      
      # together
      tmp_table <- merge(tmp_table1, tmp_table2, by=outcolnames[1], all.x=T)
      tmp_table[is.na(tmp_table[,2]), 2] <- 0
      tmp_table[is.na(tmp_table[,3]), 3] <- 0.01
      outcounts[[i]] <- tmp_table
      
    } # end for loop over columns
    
    # end if topic > 0
  } else{ # if all topics
    
    for (i in 1:length(count_cols)){
      tmp_table1 <- table(unlist(x[,count_cols[i]]))
      tmp_table1 <- data.frame(tmp_table1)
      tmp_table1[,outcolnames[3]] <- 0.01
      colnames(tmp_table1) <- outcolnames
      tmp_table1[,1] <- as.character(tmp_table1[,1])
      
      outcounts[[i]] <- tmp_table1
    }
  }
  
  names(outcounts) <- count_cols
  
  outn <- sum(x[,totalcol])
  
  out <- list('counts'=outcounts, 'nwords'=outn)
  
  return(out)
  
}



### Fightin Words model:
fightin <- function(n1, n2, counts1, counts2, priors1, priors2){
  
  # Sum of priors (alpha_0) by party
  a01 = sum(priors1)
  a02 = sum(priors2)
  
  # compute delta
  term1 = log( (counts1 + priors1) /(n1 + a01 - (counts1 + priors1)))
  term2 = log( (counts2 + priors2) /(n2 + a02 - (counts2 + priors2)))
  
  delta = term1 - term2
  
  # compute variance on delta
  vard = (1 / (counts1 + priors1)) + (1 / (counts2 + priors2) )
  
  # list of zetas (positive zetas indicate the word is associated w/ group1)
  z_scores = delta / sqrt(vard)
  
  # store total count:
  full_counts = counts1 + counts2
  
  
  return(data.frame("zeta"=z_scores, "freq"=full_counts))
}



### Fightin Words plot:
fightin_plot <- function(words, zeta, freq, groups=c("GOP","DEM"), cols=c("red2","steelblue"), nwords=15, zcut=3.29){
  
  # plot limits
  xlims <- c(-1, max(log(freq)) + 3)
  ylims <- round(max(abs(zeta)) + 5, -1)
  ylims <- c(-ylims, ylims)
  
  # xaxis labels
  xat <- c(-1, log(1), log(100), log(1000), log(10000), log(100000))
  xtics <- c("", 1, 100, 1000, 10000, 100000)
  xlab <- "Word Frequency in Topic"
  
  # ylab labels
  yrng <- ylims[2] - ylims[1]
  if (yrng > 50){
    yat <- seq(ylims[1], ylims[2], by=10)
  } else{
    yat <- seq(ylims[1], ylims[2], by = 5)
  }
  ylab <- expression(zeta[kw]^(R-D))
  
  # points to label
  tolab1 <- which(zeta %in% tail(sort(zeta), nwords) & zeta >= zcut)
  tolab2 <- which(zeta %in% head(sort(zeta), nwords) & zeta <= -zcut)
  
  # words to appear on right
  wlist1 <- which(zeta %in% tail(sort(zeta), nwords))
  wlist1 <- wlist1[order(zeta[wlist1])]
  wlist2 <- which(zeta %in% head(sort(zeta), nwords))
  wlist2 <- wlist2[order(zeta[wlist2])]
  
  par(mar = c(5,7,2,2))
  plot(0,0, type="n", xlim = xlims, ylim = ylims, xlab = xlab, ylab = ylab, cex.lab = 2, axes = F)
  axis(side = 1, at = xat, labels = xtics, cex.axis = 1.5)
  axis(side = 2, at = yat, cex.axis = 1.5)
  
  points(log(freq[abs(zeta) < zcut]), zeta[abs(zeta) < zcut], pch=21, bg="grey70", col="grey70", cex=abs(zeta[abs(zeta) < zcut]) / 3)
  points(log(freq[zeta >= zcut]), zeta[zeta >= zcut], pch=21, bg=cols[1], col=cols[1], cex=zeta[zeta >= zcut] / 3)
  points(log(freq[zeta <= -zcut]), zeta[zeta <= -zcut], pch=21, bg=cols[2], col=cols[2], cex=abs(zeta[zeta <= -zcut]) / 3)
  
  text(x = log(freq[tolab1]), y = zeta[tolab1], labels = words[tolab1], cex=zeta[tolab1] / 4, col=cols[1], pos=4)
  text(x = log(freq[tolab2]), y = zeta[tolab2], labels = words[tolab2], cex=zeta[tolab2] / 4, col=cols[2], pos=4)
  
  
  # Group labels on right
  text(x = xlims[2], y = ylims[2], labels = groups[1], col = cols[1], cex = 3, pos = 2)
  text(x = xlims[2], y = ylims[1], labels = groups[2], col = cols[2], cex = 3, pos = 2)
  
  # Group word lists
  text(x = xlims[2], y = seq(0.5, ylims[2] - 1.5, length.out = nwords), labels = words[wlist1], cex = zeta[wlist1] / 4, col = cols[1], pos = 2)
  text(x = xlims[2], y = seq(ylims[1] + 1.5, -0.5, length.out = nwords), labels = words[wlist2], cex = abs(zeta[wlist2]) / 4, col = cols[2], pos = 2)
  
  
}


### Star words that are "significant":
star <- function(words, zeta, zcut){
  
  words[abs(zeta) >= zcut] <- paste0("*", words[abs(zeta) >= zcut])
  
  return(words)
  
}


### Fightin Words plot w/o point labels and word class/group alignment indication:
fw_nowords_plot <- function(words, tagged, zeta, freq, groups=c("GOP","DEM"), classes=c("past", "future"), regexs=c("VB(D|N)","MD"), cols=c("#d7191c","#fdae61","#2b83ba","#99d594"), nwords=15, zcut=1.96, ylims=NULL, yspace=NULL, leg=NULL){
  
  ####
  ## ARGS:
  ####
  # words, vector(str): character vector of lemmas
  # tagged, vector(str): character vector of tagged lemmas
  # zeta, vector(float): vector of zeta values from Fightin' Words model
  # freq, vector(int): total frequency for each token
  # groups, (str1, str2): pair of strings naming the groups being compared
  # classes, (str1, str2): pair of strings of word classes being examined; 
  #                        first class is supposed to go with group1, second with second group;
  # regexs, (str1, str2): pair of regular expressions identifying each word class
  # cols, (str1,...,str4): colors for text and points; first color is for positive 
  #                         zeta values (i.e., group1) in class1, second for positive zetas in class2,
  #                         third for negative zetas (i.e., group2) in class2; fourth for negative 
  #                         zetas in class1
  # nwords, int: number of words to display on right-hand side of plot for each group
  # zcut, float: critical value for zeta; tokens w/ zetas below critical val have gray fill,
  #               otherwise colored according to group and class
  # ylims, (numeric, numeric): lower and upper bounds for plot (optional)
  # yspace, numeric: how far apart to place y-axis labels (optional)
  
  # plot limits
  xlims <- c(-1, max(log(freq)) + 3)
  if (is.null(ylims)){
    ylims <- round(max(abs(zeta)) + 5, -1)
    ylims <- c(-ylims, ylims)
  }
  
  # xaxis labels
  xat <- c(-1, log(1), log(100), log(1000), log(10000), log(100000))
  xtics <- c("", 1, 100, 1000, 10000, 100000)
  xlab <- "Word Frequency in Topic"
  
  # ylab labels
  if (is.null(yspace)){
    yrng <- ylims[2] - ylims[1]
    
    if (yrng > 50){
      yat <- seq(ylims[1], ylims[2], by=10)
    } else{
      yat <- seq(ylims[1], ylims[2], by=5)
    }
  } else{
    yat <- seq(ylims[1], ylims[2], by=yspace)
  }
  
  ylab <- expression(zeta[kw]^(R-D))
  
  # points to label
  tolab1 <- which(zeta %in% tail(sort(zeta), nwords) & zeta >= zcut)
  tolab2 <- which(zeta %in% head(sort(zeta), nwords) & zeta <= -zcut)
  
  # add stars to sig words
  words <- star(words, zeta, zcut)
  
  # words to appear on right
  wlist1 <- which(zeta %in% tail(sort(zeta), nwords))
  wlist1 <- wlist1[order(zeta[wlist1])]
  
  wlist2 <- which(zeta %in% head(sort(zeta), nwords))
  wlist2 <- wlist2[order(zeta[wlist2])]
  
  # getting spacing for right-side lists:
  ylist1 <- zeta[wlist1] / sum(zeta[wlist1]) #top list
  ylist1 <- (ylims[2] - 1.25) * ylist1
  ylist1 <- cumsum(ylist1)
  
  ylist2 <- zeta[wlist2] / sum(zeta[wlist2]) # bottom list
  ylist2 <- (abs(ylims[1]) - 1.25) * ylist2
  ylist2 <- cumsum(c(0, ylist2[-length(ylist2)]))
  
  # words coloring
  class1 <- grepl(pattern = regexs[1], x = tagged)
  class2 <- grepl(pattern = regexs[2], x = tagged)
  
  # label coloring
  wlist1.1 <- wlist1[which(class1[wlist1] == T)] # aligned class & group 1
  wlist1.2 <- wlist1[which(class2[wlist1] == T)] # misaligned class & group 1
  
  wlist2.1 <- wlist2[which(class2[wlist2] == T)] # aligned class & group 2
  wlist2.2 <- wlist2[which(class1[wlist2] == T)] # misaligned class & group 2
  
  # getting order for right-side lists
  worder1.1 <- which(wlist1 %in% wlist1.1)
  worder1.2 <- which(wlist1 %in% wlist1.2)
  
  worder2.1 <- which(wlist2 %in% wlist2.1)
  worder2.2 <- which(wlist2 %in% wlist2.2)
  
  # neither class
  worder1.0 <- which(wlist1 %in% wlist1.1 == F & wlist1 %in% wlist1.2 == F)
  worder2.0 <- which(wlist2 %in% wlist2.1 == F & wlist2 %in% wlist2.2 == F)
  
  wlist1.0 <- wlist1[which(wlist1 %in% wlist1.1 == F & wlist1 %in% wlist1.2 == F)]
  wlist2.0 <- wlist2[which(wlist2 %in% wlist2.1 == F & wlist2 %in% wlist2.2 == F)]
  
  
  
  
  # plot
  par(mar = c(5,7,2,2))
  plot(0,0, type="n", xlim = xlims, ylim = ylims, xlab = xlab, ylab = ylab, cex.lab = 2, axes = F)
  
  axis(side = 1, at = xat, labels = xtics, cex.axis = 1.5)
  axis(side = 2, at = yat, cex.axis = 1.5)
  
  points(log(freq[abs(zeta) < zcut]), zeta[abs(zeta) < zcut], pch=21, bg="grey70", col="grey70", cex=abs(zeta[abs(zeta) < zcut]) / 2)
  
  points(log(freq[zeta >= zcut & class1 == T]), zeta[zeta >= zcut & class1 == T], pch=21, bg=cols[1], col=cols[1], cex=zeta[zeta >= zcut & class1 == T] / 2)
  points(log(freq[zeta >= zcut & class2 == T]), zeta[zeta >= zcut & class2 == T], pch=23, bg=cols[2], col=cols[2], cex=zeta[zeta >= zcut & class2 == T] / 2)
  points(log(freq[zeta >= zcut & class1 == F & class2 == F]), zeta[zeta >= zcut & class1 == F & class2 == F], pch=21, cex=zeta[zeta >= zcut & class1 == F & class2 == F] / 2)
  
  points(log(freq[zeta <= -zcut & class2 == T]), zeta[zeta <= -zcut & class2 == T], pch=21, bg=cols[3], col=cols[3], cex=abs(zeta[zeta <= -zcut & class2 == T]) / 2)
  points(log(freq[zeta <= -zcut & class1 == T]), zeta[zeta <= -zcut & class1 == T], pch=23, bg=cols[4], col=cols[4], cex=abs(zeta[zeta <= -zcut & class1 == T]) / 2)
  points(log(freq[zeta <= -zcut & class1 == F & class2 == F]), zeta[zeta <= -zcut & class1 == F & class2 == F], pch=21, cex=zeta[zeta<= -zcut & class1 == F & class2 == F] / 2)
  
  # Group labels on right
  text(x = xlims[2], y = ylims[2], labels = groups[1], col = cols[1], cex = 3, pos = 2)
  text(x = xlims[2], y = ylims[1], labels = groups[2], col = cols[3], cex = 3, pos = 2)
  
  # Group word lists
  if (length(wlist1.0) > 0){
    text(x = xlims[2], y = (0.25 + ylist1)[worder1.0], labels = words[wlist1.0], cex = zeta[wlist1.0] / 2.5, pos = 2)
  }
  text(x = xlims[2], y = (0.25 + ylist1)[worder1.1], labels = words[wlist1.1], cex = zeta[wlist1.1] / 2.5, col = cols[1], pos = 2)
  text(x = xlims[2], y = (0.25 + ylist1)[worder1.2], labels = words[wlist1.2], cex = zeta[wlist1.2] / 2.5, col = cols[2], pos = 2)
  
  if (length(wlist2.0) > 0){
    text(x = xlims[2], y = (ylims[1] + 1 + ylist2)[worder2.0], labels = words[wlist2.0], cex = abs(zeta[wlist2.0]) / 2.5, pos = 2)
  }
  text(x = xlims[2], y = (ylims[1] + 1 + ylist2)[worder2.1], labels = words[wlist2.1], cex = abs(zeta[wlist2.1]) / 2.5, col = cols[3], pos = 2)
  text(x = xlims[2], y = (ylims[1] + 1 + ylist2)[worder2.2], labels = words[wlist2.2], cex = abs(zeta[wlist2.2]) / 2.5, col = cols[4], pos = 2)
  
  
  if (is.null(leg)){
    legend("topleft", legend = c(paste(groups[1], classes[1]), 
                                 paste(groups[1], classes[2]),
                                 paste(groups[2], classes[2]),
                                 paste(groups[2], classes[1])), 
           pch = c(21,23,21,23), pt.bg = cols, col = cols, pt.cex = 2, inset = 0.05, bty = "n")
  } 
}

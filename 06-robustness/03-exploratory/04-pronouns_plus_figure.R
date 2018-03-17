## Author: Ryan McMahon
## Date Created: 03/07/2018
## Date Last Modified: 03/15/2018
## File: "~/06-robustness/03-exploratory/04-pronouns_plus_figure.R"

## Purpose: This script examines partisan differences in pronoun use and the 
##          tokens that follow a pronoun. 
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


rm(list = ls())
options(stringsAsFactors = F)

sessionInfo()

##############################
### 0) UTILITIES
##############################


# Edited "Fightin' Words" plot:
fightin_plot <- function(words, zeta, freq, groups=c("GOP","DEM"), cols=c("red2","steelblue"), nwords=15, zcut=3.29){
  
  # plot limits
  xlims <- c(-1, max(log(freq)) + 4)
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
  ylab <- expression(zeta[w]^(R-D)/4.42)
  
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
  
  text(x = log(freq[tolab1]), y = zeta[tolab1], labels = words[tolab1], cex=zeta[tolab1] / 3, col=cols[1], pos=4)
  text(x = log(freq[tolab2]), y = zeta[tolab2], labels = words[tolab2], cex=zeta[tolab2] / 3, col=cols[2], pos=4)
  
  
  # Group labels on right
  text(x = xlims[2], y = ylims[2], labels = groups[1], col = cols[1], cex = 3, pos = 2)
  text(x = xlims[2], y = ylims[1], labels = groups[2], col = cols[2], cex = 3, pos = 2)
  
  # Group word lists
  text(x = xlims[2], y = seq(0.5, ylims[2] - 1.5, length.out = nwords), labels = words[wlist1], cex = zeta[wlist1] / 3.5, col = cols[1], pos = 2)
  text(x = xlims[2], y = seq(ylims[1] + 1.5, -0.5, length.out = nwords), labels = words[wlist2], cex = abs(zeta[wlist2]) / 3.5, col = cols[2], pos = 2)
  
  
}


##############################
### 1) LOAD DATA
##############################

## 1.0) Read in output from "/05-analysis/05-pronoun_ngram_fightin_words.py":
df <- read.csv("D:/cong_text/robust/exploratory/pronoun_ngrams_raw.csv")


##############################
### 2) TOP NGRAMS
##############################

## 3.2) Print most partisan words:
cat("\n\n\tDEMS:\n")
head(df[order(df$zeta),], 20)
cat("\n\tREPS:\n")
tail(df[order(df$zeta),], 20)


##############################
### 3) MAKE FIGURE
##############################

pdf(file = "D:/Dropbox/Dissertation/02-pos_senate/02-writing/figures/04-pronoun_plus.pdf", 
    width = 20, height = 10, encoding = "WinAnsi.enc")

fightin_plot(words = df$word, zeta = df$zeta/4.42, freq = df$count, nwords = 15, zcut = 1)

dev.off()


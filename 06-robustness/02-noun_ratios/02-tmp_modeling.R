## RBM
## 04/02/2018
## 04/17/2018

rm(list=ls())
options(stringsAsFactors = F)
library(stringr)
library(lme4)

set.seed(2222)



#########################
### 0) DEFINE FUNCTIONS
#########################


get_tags <- function(text){
  
  grams <- unlist(str_split(text, ' '))
  grams <- gsub(pattern = ".*_", replacement = '', grams)
  
  return(grams)
  
}

noun_ratio <- function(grams){
  
  n1.count <- str_count(string = grams, pattern = "(PRP[$]?|NNS?|NNPS?)(?=$)")
  n2.count <- str_count(string = grams, pattern = "(PRP[$]?|NNS?)(?=$)")
  n3.count <- str_count(string = grams, pattern = "(NNS?|NNPS?)(?=$)")
  n4.count <- str_count(string = grams, pattern = "NNS?(?=$)")
  
  
  n1.ratio <- sum(n1.count) / length(grams)
  n2.ratio <- sum(n2.count) / length(grams)
  n3.ratio <- sum(n3.count) / length(grams)
  n4.ratio <- sum(n4.count) / length(grams)
  return(c(n1.ratio, n2.ratio, n3.ratio, n4.ratio))
  
}



#########################
### 1) READ IN DATA
#########################

## 1.0) Read in text:
df <- read.csv("D:/cong_text/final_pos/topic_lemtag_merged_114.csv")

## 1.1) Read in senator meta info:
seninfo <- read.csv("D:/cong_text/robust/senator_info_links_id_female.csv")

## 1.2) Read in senator ideology:
ideo114 <- read.csv("C:/Users/Ryan McMahon/Desktop/114_ideology_govtrack.csv", encoding = "utf-8")

## 1.3) Merge senator sex into text data:
df <- merge(df, seninfo[,c("sen", "female")], by="sen", all.x = T)

# clean ideology
ideo114$name <- gsub(pattern = " ", replacement = "", x = ideo114$name)
ideo114 <- ideo114[,-c(1,5:6)]
ideo114$ideology <- ideo114$ideology - mean(ideo114$ideology)
ideo114$leadership <- ideo114$leadership - mean(ideo114$leadership)

## Merge text/sex data w/ ideology
df <- merge(x = df, y = ideo114, by.x = "lname", by.y = "name", all.x = T)

# clean party
df$gop <- ifelse(df$party=="R", 1, 0)

# time variable
df$form_date <- as.Date(df$form_date)
df$num_date <- as.numeric(df$form_date)
df$num_date <- (df$num_date - min(df$num_date)) / 90

#########################
### 2) COUNT NOUNS
#########################

cat("Counting nouns...\n")

df$ntoks <- df$nouns1 <- df$nouns2 <- df$nouns3 <- df$nouns4 <- NA

for (i in 1:nrow(df)){
  
  grams <- get_tags(text = df$lemma_text[i])
  tmp <- noun_ratio(grams = grams)
  df$ntoks[i] <- length(grams)
  df$nouns1[i] <- tmp[1]
  df$nouns2[i] <- tmp[2]
  df$nouns3[i] <- tmp[3]
  df$nouns4[i] <- tmp[4]
}

## Drop releases w/ fewer than 25 tokens:
df <- df[df$ntoks >= 25,]



mod1 <- lmer(nouns1*100 ~ ideology + gop + num_date + I(num_date^2) + I(num_date^3) + female + I(log(ntoks)) + (1|sen), data = df)
mod2 <- lmer(nouns2*100 ~ ideology + gop + num_date + I(num_date^2) + I(num_date^3) + female + I(log(ntoks)) + (1|sen), data = df)
mod3 <- lmer(nouns3*100 ~ ideology + gop + num_date + I(num_date^2) + I(num_date^3) + female + I(log(ntoks)) + (1|sen), data = df)
mod4 <- lmer(nouns4*100 ~ ideology + gop * num_date + gop *I(num_date^2) + gop *I(num_date^3) + female + I(log(ntoks)) + (1|sen), data = df)

# plot diff over time for mod 4
d <- sort(unique(df$form_date))
tmp <- seq(0, max(df$num_date), length.out = length(d))
tmpyr <- tmp*(0.774177-0.407896) + (tmp^2)*(-0.224777+0.118345) + (tmp^3)*(0.018128-0.0095) - 0.436777 + 16.432613
tmpyd <- tmp*0.774177 + (tmp^2)*-0.224777 + (tmp^3)*0.018128 + 16.432613

# This folder contains the code to run the StanfordNLP part-of-speech tagger (Toutanova et al. 2003), a basic tag correction, and morpha lemmatizer (Minnen, Carroll and Pearce 2001).


## A) How to run POS tagging (Windows 10): 

### 1. Set paths in `~/02-pos_tagging/Tagging/utils.py`:
These paths point to:
	- Input CSVs
	- Java
	- Tagger model and jar file
	- Tokenized and tagged text output folders
	
	
### 2. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

	
### 3. Navigate to the tagging folder:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\02-pos_tagging\Tagging\
```

### 4. Execute the script with a logging file:
CMD
```
(textcleaning) > python 00-nltk_tagging.py > tagging.log
```



## B) Post-tagging edits:

### 1. Failed tagging documents:
`~/cong_text/csvs/11-brown.csv` - line 3398 in ordered csv (docid=3401brown) 
	- poor parse from html
`~/cong_text/csvs/15-cardin.csv` - line 341 in ordered csv (docid=341cardin) 
	- long list of letter signatories
`~/cong_text/csvs/17-casey.csv` - line 524 in ordered csv (docid=524casey) 
	- long list of phone numbers at end
`~/cong_text/csvs/17-casey.csv` - line 816 in ordered csv (docid=816casey) 
	- long list of dollar amounts at end 

These, and all other, original parses from the HTML files are saved in the 
`~/cong_text/csvs/original_parse_csvs.7z` compressed folder. 


### 2. Incorrect tagging of parentheses:
In nearly every document parentheses, '(' and ')', were incorrectly tagged as 
being something other than parentheses (e.g., some were tagged as NNP). This 
is dealt with in the 
`~\02-pos_senate\01-code\02-pos_tagging\Tagging\01-fix_parentheses.py` 
script. All non-punctuation tags assigned to these tokens are replaced with the 
correct POS tags. 

The corrected tagged texts are saved in the `~/cong_text/csvs/tagged/fixedparenths/` 
folder while the originals are saved in the ``~/cong_text/csvs/tagged/raw.7z` 
compressed folder.




## C) Lemmatizing tagged texts:

### 1. Download and Install Morpha (PSU HPC; 64bit Linux Red Hat 6.8 - Santiago):

Note: This is taken from "Computational Methods for Corpus Annotation and 
		Analysis" (Lu 2014, 62-64).

Download these programs and place into a directory called "./programs/":
- http://personal.psu.edu/xxl13/teaching/corpus/flex-for-morph.tar.gz
- http://personal.psu.edu/xxl13/teaching/corpus/morph.tar.gz

Unpack and make the "flex-for-morph.tar.gz" folder:

BASH
```
cd ./programs/
tar -xzf flex-for-morph.tar.gz
cd flex-2.5.4
./configure
make
```


Unpack and build "morph.tar.gz":

BASH
```
cd ../
tar -xzf morph.tar.gz
cd morph
../flex-2.5.4/flex -i -Cfe -8 -omorpha.yy.c morpha.lex
gcc -o morpha morpha.yy.c
```


### 2. Formatting texts for lemmatization (local):

CMD
```
activate textcleaning
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\02-pos_tagging\Tagging\
(textcleaning) > python 02-csv2tag.py --inpath D:/cong_text/csvs/tagged/fixedparenths/ --outpath ../temp_tag/
```

Then transfer the resulting output folder to a linux system (i.e., the HPC).


### 3. Lemmatize (HPC)

BASH
```
cd work/cong_text/02-pos_tagging/programs/morph/
sh  morpha-directory.sh ../temp_tag/ -t
```

Then move the `*.lem` files to the folder `temp_lem` on local machine.



## D) Merging lemmatized text with clean tagged text csvs:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

	
### 2. Navigate to the tagging folder:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\02-pos_tagging\Tagging\
```


### 3. Execute merging script with desired options:
CMD
```
(textcleaning) > python 03-lem2csv.py --inpathcsv D:/cong_text/csvs/tagged/fixedparenths/ --inpathlem ../temp_lem/ --outpath D:/cong_text/csvs/tagged/lemmatized/
```

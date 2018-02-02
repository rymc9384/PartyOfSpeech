# This folder contains the code to extract and clean text from the raw HTMLs (scraped from the Senators' sites).

The `[NUMBER]-[NAME].py` scripts are tailored to extract the text from a particular senator. 
These are then used by the generalized `run_cleaners.py` script. 
That generalized script is called by the bash script `run_cleaners.sh`. 
This script has options regarding the removal of text that comes before and after 
the actual release (`--rmprepost`, default='y') and the removal of quotation marks (`--rmquotes`, default='n').


## A) How to run text extraction and cleaning (Windows 10):

### 1. Activate Conda Environment (probably not necessary): 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\01-clean_htmls\
```

### 3. Call shell script via Bash (need developer mode turned on for Bash):
- Make sure that the shell script calls python from the Conda environment;
	- E.g.: ~/../../mnt/c/Anaconda3/envs/textcleaning/python.exe
	
- Make sure that the shell script has end-of-line (EOL) set to UNIX; 
	- In Notepad++: Edit > EOL Conversion > UNIX (LF); save

CMD
```
(textcleaning) > bash run_cleaners.sh
```



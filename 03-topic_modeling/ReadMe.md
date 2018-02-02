# A) How to run preprocessing for ExpressedAgenda Topic Model:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\03-topic_modeling\Preprocess\
```

### 3. Call python script with desired arguments:
CMD
```
(textcleaning) > python 01-processingExpAgenda.py -o topictext_114Cong.csv --min-date 2015-01-03 > processingExpAgenda_114Cong.log
(textcleaning) > python 01-processingExpAgenda.py -o topictext_113Cong.csv --max-date 2015-01-02 > processingExpAgenda_113Cong.log
```



# B) How to run preprocessing for HDP Topic Model:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\03-topic_modeling\Preprocess\
```

### 3. Call python script with desired arguments:
CMD
```
(textcleaning) > python 02-processingHDP.py --infile topictext_114Cong.csv --outpath D:/cong_text/csvs/tokenized/topicmodeling/HDP/ --split 0.9 --outtrain hdp114_train.txt --outtest hdp114_test.txt > hdp114.log
(textcleaning) > python 02-processingHDP.py --infile topictext_113Cong.csv --outpath D:/cong_text/csvs/tokenized/topicmodeling/HDP/ --split 0.9 --outtrain hdp113_train.txt --outtest hdp113_test.txt > hdp113.log
```



# C) How to format data for the ExpressedAgenda model:

### 1. Navigate to directory with R scripts:
CMD
```
d:
cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\03-topic_modeling\ExpAgenda\
```

### 2. Call formatting script with desired arguments:
Note that there is no logging. This is because of an apparent conflict between 
specifying a log file with R CMD BATCH and the optparse library being used.

CMD
```
Rscript 00-formatting_ExpAgenda.R --infile D:/cong_text/csvs/tokenized/topicmodeling/ExpAgendas/topictext_114Cong.csv --outpath ./Processed/ --textoutfile ExpAgenda_TextDF_114.RData --processedoutfile ExpAgenda_Processed_114.RData
Rscript 00-formatting_ExpAgenda.R --infile D:/cong_text/csvs/tokenized/topicmodeling/ExpAgendas/topictext_113Cong.csv --outpath ./Processed/ --textoutfile ExpAgenda_TextDF_113.RData --processedoutfile ExpAgenda_Processed_113.RData
```



# D) How to generate the PBS scripts for estimating the Expressed Agenda model:

### 1. Navigate to directory with R scripts:
CMD
```
d:
cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\03-topic_modeling\ExpAgenda\
```

### 2. Call script to write PBS files:
CMD
```
Rscript 03-writing_PBS_scripts.R
```



# E) How to estimate the Expressed Agenda models for a given Congress:
Note that this is run on the Penn State HPC, with a Linux OS.

First, copy the processed data to the remote system (easiest with WinSCP on Windows).

BASH
```
cd work/cong_text/03-topic_modeling/ExpAgenda/
dos2unix 02-ExpAgenda_submitter.sh

cd pbs_scripts/114/
sh ../../02-ExpAgenda_submitter.sh

cd ../113/
sh ../../02-ExpAgenda_submitter.sh
```



# F) How to print out topic summaries (for selecting number of topics):

### 1. Download model fits to local machine.

### 2. Navigate to directory with R scripts
CMD
```
d:
cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\03-topic_modeling\ExpAgenda\
```

### 3. Call script selection script with desired arguments:
CMD
```
Rscript 04-select_num_topics.R --fitspath D:/cong_text/rdata/topic_modeling/model_fits/Fits/114/ --outpath ./num_topics/ --outfile select_num_topics_114.Rout
Rscript 04-select_num_topics.R --fitspath D:/cong_text/rdata/topic_modeling/model_fits/Fits/113/ --outpath ./num_topics/ --outfile select_num_topics_113.Rout
```



# G) How to fit HDP model check:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\03-topic_modeling\HDP-check\online-hdp-master\
```

### 3. Call script with desired arguments:
CMD
```
(textcleaning) > python run_online_hdp.py --T 100 --K 15 --D 43830 --W 6535 --kappa 0.6 --batchsize 2052 --max_time 1000 --seq_mode --corpus_name cong114 --data_path D:/cong_text/csvs/tokenized/topicmodeling/HDP/hdp114_train.txt --test_data_path D:/cong_text/csvs/tokenized/topicmodeling/HDP/hdp114_test.txt --directory cong114
(textcleaning) > python run_online_hdp.py --T 100 --K 15 --D 36760 --W 5675 --kappa 0.6 --batchsize 2052 --max_time 1000 --seq_mode --corpus_name cong113 --data_path D:/cong_text/csvs/tokenized/topicmodeling/HDP/hdp113_train.txt --test_data_path D:/cong_text/csvs/tokenized/topicmodeling/HDP/hdp113_test.txt --directory cong113
```



# H) How to run the Expressed Agenda replications for the 114th Congress:
Note that this is run on the Penn State HPC, with a Linux OS.

BASH
```
cd work/cong_text/03-topic_modeling/ExpAgenda/pbs_scripts/
dos2unix replication_runs_45_114.pbs

qsub replication_runs_45_114.pbs
```

You can check the job array progress with the following command:
```
qstat -u <YOUR ID>   # this is to get the $JOBID
qstat -t [$JOBID][]  # e.g., qstat -t 5012081[]
```



# I) How to evaluate replications for 114th Congress:

### 1. Download model runs to local machine.


### 2. Navigate to directory with R scripts
CMD
```
d:
cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\03-topic_modeling\ExpAgenda\
```

### 3. Call script evaluation script with desired arguments:
CMD
```
> Rscript 06-lowerbound_calc.R --reppath D:/cong_text/rdata/topic_modeling/rep_fits/Replications/114/ --processed ./Processed/ExpAgenda_Processed_114.RData --outpath ./num_topics/ --outfile lower_bounds_114.RData
```



# J) How to label topics for 114th Congress:

### 1. Navigate to directory with R scripts:
CMD
```
d:
cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\03-topic_modeling\ExpAgenda\
```

### 2. Call script evaluation script with desired arguments:
CMD
```
> Rscript 07-lb_eval_topic_labeling.R --topsumscript ./ExpAgenda-master/R/TopicSummary.R --bounds ./num_topics/lower_bounds_114.RData --textdfin ./Processed/ExpAgenda_TextDF_114.RData --tdfoutpath D:/cong_text/csvs/topics/ --tdfoutfile ExpAgenda_Topics_114.csv --toplabelpath ./topic_labeling/ --toplabelfile topic_labeling_114.csv
```

### 3. Read sampled documents and add label column to a copy of toplabelfile



# K) How to make topic summary table:

### 1. Navigate to directory with R scripts:
CMD
```
d:
cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\03-topic_modeling\ExpAgenda\
```

### 2. Call script evaluation script with desired arguments:
CMD
```
> Rscript 08-topic_table.R --bounds ./num_topics/lower_bounds_114.RData --labeled ./topic_labeling/labeled_topics_114.csv --outmodel D:/cong_text/rdata/topic_modeling/best_run_114.RData --outtable ./topic_labeling/topic_summary_table_114.csv
```
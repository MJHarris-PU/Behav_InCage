# -*- coding: utf-8 -*-
# import necessary libraries
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import os
 #%% Set some directories where scripts & files are
homeDir = "C:\\Users\mjhar\OneDrive - Princeton University\PU_RESEARCH_SPECIALIST\!BUSCHMAN_LAB\CAGE_TRAINING\!TRAINING\RIZZO2023\ColorSquareTraining"
#homeDir = "C:\\Users\mjh\OneDrive - Princeton University\PU_RESEARCH_SPECIALIST\!BUSCHMAN_LAB\CAGE_TRAINING\!TRAINING\RIZZO2023\ColorSquareTraining"
# Switch versions depending on home desktop ('mjh') or work laptop ('mjhar')
dataDir = os.path.join(homeDir,'DATA')
chartDir = os.path.join(homeDir,'Charts')
os.chdir(homeDir) # << change directory so it can access functions, etc. 
#%% IMPORT FUNCTION FROM DIRECTORY
from endBracket import endBracket
#%% Change files in data directory to have proper ']' ending
for fi in os.listdir(dataDir):
    endBracket(dataDir,fi)
#%% Steps to make dataframe
fileList = os.listdir(dataDir)
vldFiles = []
for fi in fileList:
    jsonFile = open(os.path.join(dataDir,fi)).readlines()
    if jsonFile[0] == ']':
        continue
    jsonFile = json.load(open(os.path.join(dataDir,fi)))
    if len(jsonFile) < 30:
        continue
    vldFiles.extend(jsonFile)      
#%% Make actual dataframe
DailyDF = pd.DataFrame(vldFiles)
#%% Manipulate dataframes to explode respective columns that have lists/dicts of values which need to be split up
touchPoss               = pd.DataFrame(DailyDF).explode('touchPoss')
DailyDF                 = DailyDF.explode('touchTime')
#replace 'touchPoss' column in DailyDF w/ new touchPoss DF column
DailyDF['touchPoss']    = touchPoss['touchPoss']
# Separating x & y positions to each be their own columns
DailyDF['squarePosX']   = DailyDF.apply(lambda sqx: sqx['squarePos']['x'],axis=1)
DailyDF['squarePosY']   = DailyDF.apply(lambda sqy: sqy['squarePos']['y'],axis=1)
DailyDF['touchPosX']    = DailyDF.apply(lambda tox: tox['touchPoss']['x'],axis=1)
DailyDF['touchPosY']    = DailyDF.apply(lambda toy: toy['touchPoss']['y'],axis=1)
# ^^^ COME BACK TO THIS TO FIGURE OUT HOW TO USE THE .LOC METHOD. NOT SURE RIGHT NOW...
#%% Making trialStart a datetime format & then splitting up so I can sort by unique dates
DailyDF['trialStart']   = pd.to_datetime(DailyDF['trialStart'])
DailyDF['date']         = [d.date() for d in DailyDF['trialStart']]
DailyDF['trialStart']   = [d.time() for d in DailyDF['trialStart']]
dateList                = list(DailyDF['date'].unique())
date_strings            = [str(d) for d in dateList]
#%% Establish a trial count for each day & add it toDailyDF
trlList = []
for dat in dateList:
    tempFrame           = DailyDF.loc[DailyDF['date'] == dat]
    constant            = tempFrame.index[0]
    tempFrame['trial']  = tempFrame.index-(constant-1)
    trlList.append(tempFrame['trial'].values)    
    
trlListCat              = np.concatenate(trlList)
DailyDF['trial']        = trlListCat

# ^^^ THE ABOVE CAUSES WARNING SUGGESTING .loc METHOD:
# 'A value is trying to be set on a copy of a slice from a DataFrame.
# Try using .loc[row_indexer,col_indexer] = value instead'                            
#%% Reorganize dataframe
ColList = ['date','trialStart','trial','squareSize','squarePosX','squarePosY','touchPosX','touchPosY','touchTime','rewardTime','rewardDrop']
DailyDF = DailyDF[ColList]                 
  
#%% Blues & Greens Frames
Blues = DailyDF.loc[DailyDF['rewardTime']==0,:]
Greens = DailyDF.loc[DailyDF['rewardTime']!=0,:]
                          
#%% I THINK THE DATAFRAME IS GENERALLY IN A SPOT HERE WHERE IT CAN BE PROCESSED FOR DESCRIPTIVES NOW..
#trial counts
trlCounts = [DailyDF.loc[DailyDF['date']==i,'trial'].max() for i in dateList]
BluCounts = [len(pd.unique(Blues.loc[Blues['date']==i,'trial'])) for i in dateList]
GrnCounts = [len(pd.unique(Greens.loc[Greens['date']==i,'trial'])) for i in dateList]
# example syntax that I used for this before inserting the dateList placeholder, so you can see the pd.Timestamp.date() format:
    #pd.unique(Blues.loc[Blues['date']==pd.Timestamp('2023-06-09').date(),'trial'])

#%% MAKE A GRAPH THAT SHOWS OVERALL TRIAL NUMBERS PER DAY, ALONG W/ STACKED BAR PLOT SO THE DISTRIBUTION OF GREEN VS BLUE TRIALS CAN BE VISUALIZED
fig, ax = plt.subplots()

ax.bar(date_strings,GrnCounts,color='limegreen')
ax.bar(date_strings,BluCounts,bottom=GrnCounts,color='b')

ax.plot(date_strings,trlCounts,marker='o',color='dimgrey')
# ^^ I still want to put the actual number above each of the stacks/markers ...

# Makelabels above bars
for x,y in zip(date_strings,trlCounts):
    label = "{:.0f}".format(y)
    plt.annotate(label,(x,y),textcoords="offset points",xytext=(0,10),ha='center',size='x-small')

ax.set_xlabel('Dates')
ax.set_ylabel('Trial Count')
ax.set_title('Daily Trial Counts & Distributions')
plt.yticks(np.arange(0,max(trlCounts)+50,25))
plt.xticks(date_strings,fontsize=5,rotation = 45)
plt.show()
fig.savefig(chartDir+'\TrialTracker.png')


#%% Need to figure out how many taps he is on the screen before properly executing the square...is this number getting smaller? 
# That would be the hope as it will mean that he grasping the concept of the square...
GrnTaps = []
BluTaps = []

for i in dateList:
    unqTrls = pd.unique(Greens.loc[Greens['date']==i,'trial'])
    DlyGrn=[]
    for j in unqTrls:
        DlyGrn.append(len(Greens.loc[(Greens['date']==i) & (Greens['trial']==j)]))
    GrnTaps.append(DlyGrn)
    unqTrls = pd.unique(Blues.loc[Blues['date']==i,'trial'])
    DlyBlu=[]
    for k in unqTrls:
        DlyBlu.append(len(Blues.loc[(Blues['date']==i) & (Blues['trial']==k)]))
    BluTaps.append(DlyBlu)
        #GrnTaps.append(len(Greens.loc[(Greens['date']==i) & (Greens['trial']==j)]))

# ^^^ WOULD BE GREAT TO SEE IF THERE ARE WAYS OF USING LIST COMPREHENSION TO COMPRESS THIS DOWN... ^^^       

BluTapMns   = [np.mean(i) for i in BluTaps]
BluTapMdns  = [np.median(i) for i in BluTaps]
BluTapMax   = [np.max(i) for i in BluTaps]
GrnTapMns   = [np.mean(i) for i in GrnTaps]
GrnTapMdns  = [np.median(i) for i in GrnTaps]
GrnTapMax   = [np.max(i) for i in GrnTaps]  

#%% Make Chart showing Mean number of taps per trial, green and blue, can just do line plot

fig, ax = plt.subplots()

ax.plot(date_strings,BluTapMns,marker=".",color='b')
ax.plot(date_strings,GrnTapMns,marker=".",color='limegreen')

ax.set_xlabel('Dates')
ax.set_ylabel('# of Taps')
ax.set_title('Mean Taps per Trial')

plt.xticks(date_strings,fontsize=5,rotation = 45)
plt.show()
fig.savefig(chartDir+'\MeanTrials.png')

import pandas as pd
import os
from os import path

path = os.path.relpath("data")
files = os.listdir(path)

draft, captains = [], []
# Loop function to create a list of file names for drafts and captains respectively 
for _ in files:
    if _.split()[4] == 'Draft':
        draft.append(_)
    else:
        captains.append(_)

if len(captains) != len(draft):
    print("DATA PROBLEM, there is an uneven amount of data in the '/data' folder.  There should be the same amount of Draft .csv files as there are Captains .csv files.")


# Need to map a function onto the series to change dotabuff -> userid

# Loop for captains
# file_name = "S26 Draft Sheet - Captains.csv"
print(captains)
print(len(captains))
for season in captains:
    d = pd.read_csv(f"/home/nick/programming/rd2l_pred/data/{season}")
    if d.shape[1] == 5:
        d.columns = ['Name', 'Dotabuff', 'MMR', 'Total_Money', 'Left']
        def modification(input_string):
            x = input_string.split("/")[-1]
            return x 
        d['Dotabuff'] = d['Dotabuff'].map(modification) 
        captains = [] 
        # captains.update({season.split()[0] : d})
        captains.append(d)

    # Need to figure out the above function and how to generate names for variables (Keep researching dictionary, I tried adding to a list and that didn't seem to work.  
        
    
    if d.shape[1] == 6:
        print("6 columns", season)
        continue




    # This is totally wrong not sure what is happening
    if d.shape[1] != 6 or d.shape[1] != 5:
        print("Weird Error Here", season, d.shape)
        continue
   
    
    print(captains)
    # captains = {}
    # captains.update({season.split()[0] : d})

# DataFrame analysis starts here: 
# print(d.loc[:, "Buck's Bucks"].mean())
# print(d.loc[:, "Buck's Bucks"].describe())



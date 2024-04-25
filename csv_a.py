import pandas as pd
import os
from os import path

file_name = "S25 Draft Sheet - Captains.csv"
d = pd.read_csv(f"/home/nick/programming/rd2l_pred/data/{file_name}", header=0)

# print(d)
# print(d.head())
# print(type(d))]
# print(d.index)
print(d.loc[:, "Buck's Bucks"].mean())

path = os.path.relpath("data")
files = os.listdir(path)
draft, captains = [], []
# Loop function to create a list of file names for drafts and captains respectively 
# for _ in files:
#     if     

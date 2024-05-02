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

draft = sorted(draft)
captains = sorted(captains)


# Need to map a function onto the series to change dotabuff -> userid

# Loop to gather the monetary information for the league season 
def modification(input_string):
    x = input_string.split("/")[-1]
    return x 

money = {}
for season in captains:
    #TODO This should be changed to a relative directory instead of using user specifid (Already have os)
    d = pd.read_csv(f"/home/spiffy/programming/rd2l_pred/data/{season}")

    if d.shape[1] == 5:
        d.columns = ['Name', 'Dotabuff', 'MMR', 'Total_Money', 'Left']
        d['Dotabuff'] = d['Dotabuff'].map(modification) 
        s = pd.Series(data={'sum': d.Total_Money.sum()}, index=['sum'])
        money.update({season.split()[0] : pd.concat([d.Total_Money.describe(), s])})
    
    if d.shape[1] == 6:
        d.columns = ['Name', 'Dotabuff', 'MMR', 'Fake Money', 'Total_Money', 'Left']
        d = d.drop('Fake Money', axis=1)
        d['Dotabuff'] = d['Dotabuff'].map(modification) 
        s = pd.Series(data={'sum': d.Total_Money.sum()}, index=['sum'])
        money.update({season.split()[0] : pd.concat([d.Total_Money.describe(), s])})

    if d.shape[1] != 6 and d.shape[1] != 5:
        print("Weird Error Here", season, d.shape)
        continue
# print(money)
players_dict = {}
for season in draft:
    #TODO This should be changed to a relative directory instead of using user specifid (Already have os)
    d = pd.read_csv(f"/home/spiffy/programming/rd2l_pred/data/{season}")
    d = d.drop(columns=['Winner:', 'Discord ID:', 'Player statement: '])
    # This is a temporary fix to accomodate the random 'statement' in the sheets file.
    d = d.iloc[:56]
    d['Dotabuff Link:'] = d['Dotabuff Link:'].map(modification)
    d = d.rename(columns={"Cost:": "cost", "Dotabuff Link:": "player_id", "MMR:": "mmr", "Comfort (Pos 1):": "p1", "Comfort (Pos 2):": "p2", "Comfort (Pos 3):": "p3", "Comfort (Pos 4):": "p4", "Comfort (Pos 5):": "p5"})
    # Turning the comfort levels into binary classification might be something worth exploring
    player_season = season.split(" ")[0]
    # print(money[player_season])
    # print(money[player_season].shape)
    # print((money[player_season].loc['count']))
    d = d.assign(count=lambda x: money[player_season].loc['count'], mean=lambda x: money[player_season].loc['mean'], std=lambda x: money[player_season].loc['std'], min=lambda x: money[player_season].loc['min'], max=lambda x: money[player_season].loc['max'], sum=lambda x: money[player_season].loc['sum'])
    for players in range(len(d.player_id.to_list())):
        p_id = d.iloc[players, 1]
        players_dict.update({f"{p_id}_{player_season}": d.iloc[players]})
        # print(f"{p_id}_{player_season}")
    print(len(players_dict))
final_df = pd.DataFrame(data=players_dict)
print(final_df)
final_df.to_csv('output/spreadsheet_info.csv')
# final_df.to_csv('output/spreadsheet_info.csv', index=False)
   
# print(d)
# print(d.iloc[0])



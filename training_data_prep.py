import pandas as pd
import os
from os import path


def list_format(location):
    """Parses the information within the data folder and returns a list with the respective file names"""
    path = os.path.relpath(f"{location}")
    files = os.listdir(path)
    draft, captains = [], []
    
    # Loop function to create a list of file names for drafts and captains respectively 
    for _ in files:
        if _ == 'INSTRUCTIONS.md':
            pass
        elif _.split()[4] == 'Draft':
            draft.append(_)
        else:
            captains.append(_)
    
    # Prints an Error if the information doesn't align
    # TODO implement question asking the user if they want to skip over files that do not align
    if len(captains) != len(draft):
        print("DATA PROBLEM, there is an uneven amount of data in the '/data' folder.  There should be the same amount of Draft .csv files as there are Captains .csv files.")
    
    # If you don't sort the data, the two lists don't line up
    draft = sorted(draft)
    captains = sorted(captains)
    
    return draft, captains



def modification(input_string):
    """Maps a function onto the series to change dotabuff -> userid"""
    x = input_string.split("/")[-1]
    return x 

def league_money(captains, data_type):
    """Loop to gather the monetary information for the league season"""
    
    money = {}
    for season in captains:
        #TODO This should be changed to a relative directory instead of using user specifid (Already have os)

        if data_type == 'prediction':
            path = os.path.relpath(f"input/{season}")
        elif data_type == 'training':
            path = os.path.relpath(f"data/{season}")

        d = pd.read_csv(path)
    
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
    return money


def df_gen(draft, money, data_type):
    """Generates the dataframe containing all players"""

    players_dict = {}
    for season in draft:

        # Reads the .csv file for the selected season
        if data_type == 'prediction':
            path = os.path.relpath(f"input/{season}")
        elif data_type == 'training':
            path = os.path.relpath(f"data/{season}")
        d = pd.read_csv(path)


        # Removes columns that are not needed
        d = d.drop(columns=['Winner:', 'Discord ID:', 'Player statement: '])

        # Maps the dotabuff -> steam_id conversion
        d['Dotabuff Link:'] = d['Dotabuff Link:'].map(modification)

        d = d.rename(columns={"Cost:": "cost", "Dotabuff Link:": "player_id", "MMR:": "mmr", "Comfort (Pos 1):": "p1", "Comfort (Pos 2):": "p2", "Comfort (Pos 3):": "p3", "Comfort (Pos 4):": "p4", "Comfort (Pos 5):": "p5"})

        #TODO Explore turning the comfort levels into binary classification 

        # Grabs season number from the file name
        player_season = season.split(" ")[0]

        d = d.assign(count=lambda x: money[player_season].loc['count'], mean=lambda x: money[player_season].loc['mean'], std=lambda x: money[player_season].loc['std'], min=lambda x: money[player_season].loc['min'], max=lambda x: money[player_season].loc['max'], sum=lambda x: money[player_season].loc['sum'])


        for players in range(len(d.player_id.to_list())):
            p_id = d.iloc[players, 1]
            players_dict.update({f"{p_id}_{player_season}": d.iloc[players]})
    
    final_df = pd.DataFrame(data=players_dict)
    # Prints the Transposed version of the DataFrame
    print(final_df.transpose())

    # TODO Should create a directory called /data/staging/ where the prepped data is stored.

    os.makedirs("output", exist_ok=True)
    
    if data_type == 'prediction':
        path = os.path.relpath('output/prediction_data_prepped.csv')
        final_df.to_csv(path)

    elif data_type == 'training':
        path = os.path.relpath('output/training_data_prepped.csv')
        final_df.to_csv(path)


if __name__ == "__main__":
    data_type = 'training'
    draft, captains = list_format("data")
    league_money(captains, data_type) 
    df_gen(draft, league_money(captains, data_type), data_type)
    print(f"{data_type.capitalize()} Data was successfully prepared")

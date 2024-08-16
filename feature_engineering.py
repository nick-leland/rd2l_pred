import requests
import pandas as pd
import time
import sys
import os
from os import path
import io


def heroes(player_id):
    """Gets the statistics of heroes that player_id has played"""
    url = f"https://api.opendota.com/api/players/{player_id}/heroes"
    payload = ""
    headers = {"User-Agent": "insomnia/8.6.1"}
    response = requests.request("GET", url, data=payload, headers=headers)
    return response.text


def hero_information(player):
    """Creates a series for each player"""
    x = heroes(player)  
    # Gets heroes for player, if trouble reaching server, waits 10 seconds before attempting again.
    while x == """{"error":"Internal Server Error"}""":
        print("There is an issue reaching the Open Dota API")
        time.sleep(10)
        x = heroes(player)
    # Convert to StringIO before passing into pandas, can't take json directly
    y = io.StringIO(x)
    d = pd.read_json(y)

    # Currently drop this information but it might be useful for matchup analysis
    d = d.drop(["last_played", "with_games", "with_win", "against_games", "against_win"], axis=1)

    played_heroes = d.sort_values('hero_id')
    d = d.assign(winrate=lambda x: x.win/x.games)

    # Any NaN data here just means they haven't played that hero, so it gets replaced with a 0.
    d = d.fillna(0)
    general = {}
    general['total_games_played'] = d.games.sum()

    # Detects if the player has a private account
    if d.win.sum() == 0 and d.games.sum() ==0:
        raise TypeError("Players information is private")

    general['total_winrate'] = d.win.sum() / d.games.sum()
    ser = pd.Series(data=general, index=['total_games_played', 'total_winrate'])

    games_pivot = d.pivot_table(index=None, columns='hero_id', values='games', aggfunc='sum')
    winrate_pivot = d.pivot_table(index=None, columns='hero_id', values='winrate', aggfunc='mean')

    games_pivot.columns=[f'games_{hero_id}' for hero_id in games_pivot.columns]
    winrate_pivot.columns=[f'winrate_{hero_id}' for hero_id in winrate_pivot.columns]

    final_df = pd.concat([games_pivot, winrate_pivot], axis=1)

    columns_sorted = sorted(final_df.columns, key=lambda x: (int(x.split('_')[1]), x.split('_')[0]))
    final_df = final_df.reindex(columns=columns_sorted)
    single_row = final_df.apply(lambda x: x.dropna().reset_index(drop=True)[0])

    final = pd.concat([ser, single_row])
    return final


# TODO Impliment an offline testing version of this which saves the dataframes as pickle documents, read here: https://stackoverflow.com/questions/17098654/how-to-reversibly-store-and-load-a-pandas-dataframe-to-from-disk 


if __name__ == "__main__":
    # Defines our output that we will save to a file
    output = {}

    # TODO Work on this section and get it ready for integration and managing of both file types
    os.makedirs("output", exist_ok=True)
    path = os.path.relpath("output")
    files = os.listdir(path)

    print(f"Generate [t]raining data if you want to train on a custom dataset.")
    print(f"Generate [p]rediction data if you want to make predictions on a new season.")
    print(f"Generate [b]oth if you want to generate fresh data using both train and test inputs.\n")
    choice = input("Do you want to generate [t]raining data [p]rediction data or [b]oth?\n")

    # Remove the files based on the given situation.
    if choice == 'p' or choice == 'prediction':
        files.remove("training_data_prepped.csv")

    if choice == 't' or choice == 'training' or choice == 'train':
        files.remove("prediction_data_prepped.csv")

    # If user wants both, we should maybe try threading?
    # Otherwise, threading would be good for running multiple API's together

    # Loop through the rest of the files in the folder structure.
    for csv in files:

        # Split the name to filter through the result files
        name = csv.split("_")[0].title()
        # This can be added upon, currently only skipping over the results of this function
        if name == "Result":
            pass 
        else:
            # Define the path of the file 
            location = path + "/" + csv
            print(f"Working on {name} data.")

            # Read the csv file at the above location
            df = pd.read_csv(location, index_col=0).transpose()

            # Create a list for the players within the csv file
            players = df.loc[:, 'player_id'].to_list()

            # Prompt the user before parsing for data.
            print(f"There are {len(players)} players to parse in {name}.  Do you want to continue? ")
            choice = input("[y]es or [n]o?\n")

            if choice == 'n' or choice == 'no':
                sys.exit()

            for _ in range(len(players)):
                try: 
                    # Adds the hero information for the players
                    output.update({df.iloc[_].name: pd.concat([df.iloc[_], hero_information(str(int(players[_])))])})

                    # Determines the users player_id for debugging
                    player_id = df.iloc[_].name
                    print(f"Completed {player_id}")

                    # Sets a delay due to API limitations
                    time.sleep(2)

                except ValueError:
                    # Look more into this, not sure why we would get a ValueError
                    print("ValueError on {players[_]}")
                    pass
                except TypeError:
                    print(f"{players[_]} has a private account")
                    pass
            all_info = pd.DataFrame.from_dict(output)
            all_info.to_csv(f'output/result_{csv}')
            print(f"Saved to 'output/result_{csv}'")



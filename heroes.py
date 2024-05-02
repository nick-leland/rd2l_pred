import requests
import pandas as pd
import time
import sys


def heroes(player_id):
    """Gets the statistics of heroes that player_id has played"""
    url = f"https://api.opendota.com/api/players/{player_id}/heroes"
    payload = ""
    headers = {"User-Agent": "insomnia/8.6.1"}
    response = requests.request("GET", url, data=payload, headers=headers)
    return response.text


def hero_information(player):
    x = heroes(player)
    while x == """{"error":"Internal Server Error"}""":
        print("There is an issue reaching the Open Dota API")
        time.sleep(10)
        x = heroes(player)
    d = pd.read_json(x)
    d = d.drop(["last_played", "with_games", "with_win", "against_games", "against_win"], axis=1)

    played_heroes = d.sort_values('hero_id')
    d = d.assign(winrate=lambda x: x.win/x.games)

    d = d.fillna(0)
        
    general = {}
    general['total_games_played'] = d.games.sum()
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
    output = {}
    df = pd.read_csv("output/spreadsheet_info.csv", index_col=0).transpose()
    players = df.loc[:, 'player_id'].to_list()
    for _ in range(len(players)):
        try: 
            output.update({df.iloc[_].name: pd.concat([df.iloc[_], hero_information(str(int(players[_])))])})
            player_id = df.iloc[_].name
            print(f"Completed {player_id}")
            time.sleep(2)
            all_info = pd.DataFrame.from_dict(output)
            all_info.to_csv('output/all_info.csv')
        except ValueError:
            print("ValueError on {_}")
            pass
        except TypeError:
            print("{_} has a private account")
            pass


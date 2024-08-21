import requests
import pandas as pd
import time
import sys
import os
from os import path
import io
from dotenv import load_dotenv
import json

def stratz_request(players):
    url = "https://api.stratz.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('STRATZ_API_KEY')}"
    }
    # This query is 9 tokens.
    # I want to identify the token count just based on the query
    # Using token count, automatically generate a time delay to allocate limits.

    # Hero IMP is important, average IMP per game on each hero might be more important.
    query = f"""
    {{
      players(steamAccountIds: {str(players)}) {{
        steamAccount {{id}}
        matchCount
        winCount
        behaviorScore
        activity {{
          activity
        }}
        performance {{
          imp
          rank
          kills
          killsAverage
          deaths
          deathsAverage
          assists
          assistsAverage
          cs
          csAverage
          gpm
          gpmAverage
          xpm
          xpmAverage
        }}
        heroesPerformance {{
          kDA
          avgKills
          avgDeaths
          avgAssists
          imp
          best
          lastPlayedDateTime
        }}
        ranks {{
          seasonRankId
          asOfDateTime
          isCore
          rank
        }}
        matches(request: {{leagueIds: {str(leagues)} }}) {{
          didRadiantWin
        }}
      }}
    }}
    """
    testing = json.dumps(query)
    response = requests.post(url, json={'query': query}, headers=headers)
    return response.json()

if __name__ == "__main__":
    players = [27676663, 80266369]
    load_dotenv()
    leagues = [15578]
    print(stratz_request(players))

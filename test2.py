# import time
import pandas as pd
import requests

# print("Start")
# time.sleep(5)
# print("500 delay")

# r = requests.get('https://api.opendota.com/api/heroes').json()

# r = requests.get('https://api.opendota.com/api/leagues/65006/matches').json()

r = requests.get('https://api.opendota.com/api/leagues/15576/matches').json()

print(r)

df = pd.DataFrame(r)

# print(df)
# print(df.head())
# print(df.localized_name) # This is a series

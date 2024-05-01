import requests

url = "https://api.opendota.com/api/players/162015739/matches"

querystring = {"significant":"0","project":["duration","game_mode","lobby_type","start_time","hero_id","version","kills","deaths","assists","leaver_status","party_size","average_rank","item_0","item_1","item_2","item_3","item_4","item_5"]}

payload = ""
headers = {"User-Agent": "insomnia/8.6.1"}

response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

print(response.text)
print(type(response.text))

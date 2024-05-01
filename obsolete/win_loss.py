import requests

def winloss(player_id):
    url = f"https://api.opendota.com/api/players/{player_id}/wl"

    payload = ""
    headers = {"User-Agent": "insomnia/8.6.1"}

    response = requests.request("GET", url, data=payload, headers=headers)

    print(response.text)

if __name__ == "__main__":
    winloss(162015739)

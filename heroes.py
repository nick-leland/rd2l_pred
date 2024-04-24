import requests

def heroes(player_id):
    url = f"https://api.opendota.com/api/players/{player_id}/heroes"

    payload = ""
    headers = {"User-Agent": "insomnia/8.6.1"}

    response = requests.request("GET", url, data=payload, headers=headers)

    # print(response.text)
    # response.text is a string
    print(response)
    print(type(response))



    

if __name__ == "__main__":
    heroes(162015739)

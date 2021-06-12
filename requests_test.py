from typing import KeysView
import requests
def grab_manga_id(title: str) -> str:
    title.replace(' ', '+')
    try:
        response = requests.get(f"https://api.mangadex.org/manga?title={title}]")
        data = response.json()
        id = data['results'][0]['data']['id']
    except:
        id = "Manga Not Found"
    return id

def grab_manga_description(title: str) -> str:
    title.replace(' ', '+')
    try:
        response = requests.get(f"https://api.mangadex.org/manga?title={title}]")
        data = response.json()
        desc = data['results'][0]['data']['attributes']['description']['en']
    except:
        desc = "Manga Not Found"   
    return desc

print(grab_manga_description('Berserk'))
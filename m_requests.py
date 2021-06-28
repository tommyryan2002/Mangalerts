from typing import KeysView
import requests
def grab_manga_id(title: str) -> str:
    title.replace(' ', '+')
    try:
        response = requests.get(f"https://api.mangadex.org/manga?title={title}]")
        data = response.json()
        id = data['results'][0]['data']['id']
    except:
        id = None
    return id

def grab_manga_title(title: str) -> str:
    title.replace(' ', '+')
    try:
        response = requests.get(f"https://api.mangadex.org/manga?title={title}]")
        data = response.json()
        title = data['results'][0]['data']['attributes']['title']['en']
    except:
        title = "Manga Not Found"
    return title

def grab_manga_description(title: str) -> str:
    title.replace(' ', '+')
    try:
        response = requests.get(f"https://api.mangadex.org/manga?title={title}]")
        data = response.json()
        desc = data['results'][0]['data']['attributes']['description']['en']
    except:
        desc = "Manga Not Found"   
    return desc

def grab_cover_id(id: str) -> str:
    try:
       response = requests.get(f"https://api.mangadex.org/cover?manga[]={id}")
       data = response.json()
       cover_id = data['results'][0]['data']['attributes']['fileName']
    except:
        cover_id = None
    return cover_id

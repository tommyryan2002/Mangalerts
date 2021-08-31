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
        title = data['results'][0]['data']['attributes']['title']
    except:
        title = "Manga Not Found"
    return list(title.items())[0][1]

def grab_manga_description(title: str) -> str:
    title.replace(' ', '+')
    try:
        response = requests.get(f"https://api.mangadex.org/manga?title={title}]")
        data = response.json()
        desc = data['results'][0]['data']['attributes']['description']['en']
    except:
        desc = "Manga Not Found"   
    return desc

def grab_manga_rating(title:str):
    try:
        response = requests.get(f"https://api.mangadex.org/manga?title={title}]")
        data = response.json()
        rating = data['results'][0]['data']['attributes']['contentRating']
    except:
        rating = "Manga Not Found"
    return rating

def grab_cover_id(id: str) -> str:
    try:
       response = requests.get(f"https://api.mangadex.org/cover?manga[]={id}")
       data = response.json()
       cover_id = data['results'][0]['data']['attributes']['fileName']
    except:
        cover_id = None
    return cover_id
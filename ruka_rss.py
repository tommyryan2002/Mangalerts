import feedparser
import re
d = feedparser.parse('https://www.mangaupdates.com/rss.php')
def grab_rss_data():
    manga_array = []
    for ele in d['entries']:
        chapter = re.search(r"(v.\d{1,} )?c.\d{1,}(\.\d)?(-\d{1,}(\.\d)?)?", ele['title']).group()
        len_chap = len(chapter)
        raw_title = ele['title']
        char = raw_title[0]
        scan_group = ''
        while char != "]":
            if char not in ["[", "]"]:
                scan_group += char
            raw_title = raw_title[1:]
            char = raw_title[0]
        raw_title = raw_title[1: len(raw_title) - len_chap - 2]
        manga_array.append({'title': raw_title, 'group': scan_group, 'chapter': chapter})
    return manga_array
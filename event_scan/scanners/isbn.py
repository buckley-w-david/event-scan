from urllib.request import urlopen
import json

from datetime import datetime

from event_scan.event import Event

def scan(config, isbn):
    with urlopen(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={config.books_secret}') as req:
        resp = json.load(req)

    for item in resp['items']:
        if any(id['identifier'] == isbn for id in item['volumeInfo']['industryIdentifiers']):
            published = datetime.strptime(item['volumeInfo']['publishedDate'], '%Y-%m-%d')
            url = item['volumeInfo']['canonicalVolumeLink']
            authors = ', '.join(item['volumeInfo']['authors'])
            title = f"{item['volumeInfo']['title']} by {authors} is out!"
            description = item['volumeInfo']['description']

            return published < datetime.now(), Event(
                url=url,
                title=title,
                description=description,
                date=published,
            )


    return False, None

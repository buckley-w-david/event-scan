from pathlib import Path
import typer
import toml

from dataclasses import dataclass
from datetime import timezone

from sqlalchemy import text

from event_scan import db
from event_scan import scanners

@dataclass
class EventScanConfig:
    db: str
    books_secret: str

    feed_url: str
    feed_path: str

app = typer.Typer()

@app.command()
def add(data_type: str, data: str, once: bool = False, config_file: Path = Path('config.toml')):
    config = EventScanConfig(**toml.load(config_file))

    with db.connect(config.db) as conn:
        res = db.add_source(conn, data_type, data, once)

    print(res)

@app.command()
def scan(config_file: Path = Path('config.toml')):
    config = EventScanConfig(**toml.load(config_file))

    with db.connect(config.db) as conn:
        for (source_id, data_type, data) in db.get_scan_sources(conn):
            scanner = getattr(scanners, data_type)
            trigger, event = scanner.scan(config, data)
            if trigger:
                db.add_event(conn, source_id, event)

from feedgen.feed import FeedGenerator

@app.command()
def generate(config_file: Path = Path('config.toml')):
    config = EventScanConfig(**toml.load(config_file))

    rss_feed = FeedGenerator()

    rss_feed.id(config.feed_url)
    rss_feed.title('Events!')
    rss_feed.author({
        'name': 'David Buckley',
        'email': 'david@davidbuckley.ca'
    })
    rss_feed.description('Events!')
    rss_feed.link( href=config.feed_url, rel='alternate' )
    rss_feed.language('en')

    with db.connect(config.db) as conn:
        for event in db.get_events(conn):
            feed_entry = rss_feed.add_entry()
            feed_entry.id(event.url)
            feed_entry.title(event.title)
            feed_entry.description(event.description)
            feed_entry.link( href=event.url, rel='alternate' )
            feed_entry.published(event.date.replace(tzinfo=timezone.utc))

    rss_feed.rss_file(config.feed_path)

@app.command()
def run(config_file: Path = Path('config.toml')):
    scan(config_file)
    generate(config_file)

if __name__ == '__main__':
    app()

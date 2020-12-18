import contextlib

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import text, select

from event_scan.event import Event

metadata = MetaData()
sources = Table('sources', metadata,
    Column('source_id', Integer, primary_key=True),
    Column('data_type', String),
    Column('data', String),
    Column('once', Boolean),
)

events = Table('events', metadata,
    Column('event_id', Integer, primary_key=True),
    Column('source_id', None, ForeignKey('sources.source_id')),
    Column('url', String, nullable=False),
    Column('title', String, nullable=False),
    Column('description', String, nullable=False),
    Column('event_date', DateTime, nullable=False),
)

@contextlib.contextmanager
def connect(connection_string):
    engine = create_engine(connection_string)
    metadata.create_all(engine)
    try:
        with engine.connect() as conn:
            yield conn
    finally:
        engine.dispose()

def add_source(conn, data_type: str, data: str, once: bool):
    return conn.execute(sources.insert(), data_type=data_type, data=data, once=once)

def add_event(conn, source_id: str, event: Event):
    return conn.execute(
        events.insert(),
        source_id=source_id,
        url=event.url,
        title=event.title,
        description=event.description,
        event_date=event.date
    )

def get_scan_sources(conn):
    query = text(
        '''
        SELECT sources.source_id, sources.data_type, sources.data FROM sources
          LEFT OUTER JOIN events ON sources.source_id = events.source_id
        WHERE NOT sources.once OR events.source_id IS NULL
        '''
    )

    for result in conn.execute(query):
        yield result

def get_events(conn):
    for result in conn.execute(select([events.c.url, events.c.title, events.c.description, events.c.event_date])):
        yield Event(
            url=result.url,
            title=result.title,
            description=result.description,
            date=result.event_date
        )

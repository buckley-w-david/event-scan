from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    url: str
    title: str
    description: str
    date: datetime

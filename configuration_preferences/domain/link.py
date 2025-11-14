from dataclasses import dataclass
from datetime import datetime

@dataclass
class LinkEntity:
    blind_user_id: str
    link_code: str
    created_at: datetime
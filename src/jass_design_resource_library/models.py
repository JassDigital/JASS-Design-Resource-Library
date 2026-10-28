from dataclasses import dataclass
@dataclass
class Resource:
    id: int | None = None
    name: str = ""
    category: str = "Other"
    description: str = ""
    url: str = ""
    platform: str = "Web"
    pricing: str = "Unknown"
    licence: str = "Check provider"
    status: str = "Not checked"
    tags: str = ""
    favorite: bool = False
    notes: str = ""

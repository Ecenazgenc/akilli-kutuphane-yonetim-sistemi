"""
Category Entity - Kategori Veri Modeli
"""

from dataclasses import dataclass


@dataclass
class Category:
    """Kategori Entity"""
    Id: int
    Name: str
    
    def to_dict(self) -> dict:
        """Entity'yi dictionary'e çevirir"""
        return {
            "id": self.Id,
            "name": self.Name
        }

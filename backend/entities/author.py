"""
Author Entity - Yazar Veri Modeli
"""

from dataclasses import dataclass


@dataclass
class Author:
    """Yazar Entity"""
    Id: int
    Name: str
    LastName: str
    Country: str
    
    def to_dict(self) -> dict:
        """Entity'yi dictionary'e çevirir"""
        return {
            "id": self.Id,
            "name": self.Name,
            "lastName": self.LastName,
            "country": self.Country,
            "fullName": f"{self.Name} {self.LastName}"
        }

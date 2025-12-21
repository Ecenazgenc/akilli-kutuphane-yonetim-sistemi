"""
Book Entity - Kitap Veri Modeli
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    """Kitap Entity"""
    Id: int
    Title: str
    AuthorId: int
    CategoryId: int
    StockNumber: int
    YearOfpublication: int
    AuthorName: Optional[str] = None
    CategoryName: Optional[str] = None
    Available: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Entity'yi dictionary'e çevirir"""
        return {
            "id": self.Id,
            "title": self.Title,
            "authorId": self.AuthorId,
            "categoryId": self.CategoryId,
            "stockNumber": self.StockNumber,
            "yearOfPublication": self.YearOfpublication,
            "authorName": self.AuthorName or "",
            "categoryName": self.CategoryName or "",
            "available": self.Available if self.Available is not None else self.StockNumber
        }
    
    def is_available(self) -> bool:
        """Kitap mevcut mu kontrol eder"""
        avail = self.Available if self.Available is not None else self.StockNumber
        return avail > 0

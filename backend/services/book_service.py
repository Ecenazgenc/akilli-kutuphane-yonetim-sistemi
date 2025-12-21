"""
Book Service - Kitap İş Mantığı
"""

from typing import List, Optional
from repositories import BookRepository
from entities import Book


class BookService:
    """Kitap servisi"""
    
    def __init__(self):
        self.repo = BookRepository()
    
    def get_all(self) -> List[Book]:
        return self.repo.get_all()
    
    def get_by_id(self, book_id: int) -> Optional[Book]:
        return self.repo.get_by_id(book_id)
    
    def create(self, title: str, author_id: int, category_id: int, stock: int, year: int) -> Optional[Book]:
        return self.repo.add(title, author_id, category_id, stock, year)
    
    def update(self, book_id: int, title: str, author_id: int, category_id: int, stock: int, year: int) -> bool:
        return self.repo.update(book_id, title, author_id, category_id, stock, year)
    
    def delete(self, book_id: int) -> bool:
        return self.repo.delete(book_id)


# Singleton instance
book_service = BookService()

"""AUTHOR_SERVICE.PY - Yazar Servisi"""
from typing import List, Optional
from repositories.author_repository import AuthorRepository
from entities.author import Author

class AuthorService:
    def __init__(self):
        self.repo = AuthorRepository()
    
    def get_all(self) -> List[Author]:
        return self.repo.get_all()
    
    def get_by_id(self, author_id: int) -> Optional[Author]:
        return self.repo.get_by_id(author_id)
    
    def create(self, name: str, lastname: str, country: str) -> Optional[Author]:
        return self.repo.add(name, lastname, country)
    
    def update(self, author_id: int, name: str, lastname: str, country: str) -> bool:
        return self.repo.update(author_id, name, lastname, country)
    
    def delete(self, author_id: int) -> bool:
        return self.repo.delete(author_id)

author_service = AuthorService()

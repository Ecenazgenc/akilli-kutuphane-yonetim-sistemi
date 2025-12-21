"""
Category Service - Kategori İş Mantığı
"""

from typing import List, Optional
from repositories import CategoryRepository
from entities import Category


class CategoryService:
    """Kategori servisi"""
    
    def __init__(self):
        self.repo = CategoryRepository()
    
    def get_all(self) -> List[Category]:
        return self.repo.get_all()
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.repo.get_by_id(category_id)
    
    def create(self, name: str) -> Optional[Category]:
        return self.repo.add(name)
    
    def update(self, category_id: int, name: str) -> bool:
        return self.repo.update(category_id, name)
    
    def delete(self, category_id: int) -> bool:
        return self.repo.delete(category_id)


# Singleton instance
category_service = CategoryService()

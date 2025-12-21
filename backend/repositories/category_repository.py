"""
Category Repository - Kategori Veritabanı İşlemleri
"""

from typing import List, Optional
from .base_repository import BaseRepository
from entities import Category


class CategoryRepository(BaseRepository):
    """Kategori Repository"""
    
    def get_all(self) -> List[Category]:
        """Tüm kategorileri getirir"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Name FROM Categories")
            categories = []
            for row in cursor.fetchall():
                categories.append(Category(Id=row[0], Name=row[1]))
            conn.close()
            return categories
        except Exception as e:
            print(f"CategoryRepository.get_all error: {e}")
            return []
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """ID ile kategori getirir"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Name FROM Categories WHERE Id = ?", category_id)
            row = cursor.fetchone()
            conn.close()
            if row:
                return Category(Id=row[0], Name=row[1])
            return None
        except Exception as e:
            print(f"CategoryRepository.get_by_id error: {e}")
            return None
    
    def add(self, name: str) -> Optional[Category]:
        """Yeni kategori ekler"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Categories (Name) VALUES (?); SELECT SCOPE_IDENTITY();", name)
            cursor.nextset()
            new_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return Category(Id=int(new_id), Name=name)
        except Exception as e:
            print(f"CategoryRepository.add error: {e}")
            return None
    
    def update(self, category_id: int, name: str) -> bool:
        """Kategori günceller"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Categories SET Name = ? WHERE Id = ?", name, category_id)
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0
        except Exception as e:
            print(f"CategoryRepository.update error: {e}")
            return False
    
    def delete(self, category_id: int) -> bool:
        """Kategori siler"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Categories WHERE Id = ?", category_id)
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0
        except Exception as e:
            print(f"CategoryRepository.delete error: {e}")
            return False

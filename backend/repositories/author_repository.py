"""
Author Repository - Yazar Veritabanı İşlemleri
"""

from typing import List, Optional
from .base_repository import BaseRepository
from entities import Author


class AuthorRepository(BaseRepository):
    """Yazar Repository"""
    
    def get_all(self) -> List[Author]:
        """Tüm yazarları getirir"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Name, LastName, Country FROM Authors")
            authors = []
            for row in cursor.fetchall():
                authors.append(Author(Id=row[0], Name=row[1], LastName=row[2], Country=row[3]))
            conn.close()
            return authors
        except Exception as e:
            print(f"AuthorRepository.get_all error: {e}")
            return []
    
    def get_by_id(self, author_id: int) -> Optional[Author]:
        """ID ile yazar getirir"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Name, LastName, Country FROM Authors WHERE Id = ?", author_id)
            row = cursor.fetchone()
            conn.close()
            if row:
                return Author(Id=row[0], Name=row[1], LastName=row[2], Country=row[3])
            return None
        except Exception as e:
            print(f"AuthorRepository.get_by_id error: {e}")
            return None
    
    def add(self, name: str, lastname: str, country: str) -> Optional[Author]:
        """Yeni yazar ekler"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Authors (Name, LastName, Country) VALUES (?, ?, ?); SELECT SCOPE_IDENTITY();",
                name, lastname, country
            )
            cursor.nextset()
            new_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return Author(Id=int(new_id), Name=name, LastName=lastname, Country=country)
        except Exception as e:
            print(f"AuthorRepository.add error: {e}")
            return None
    
    def update(self, author_id: int, name: str, lastname: str, country: str) -> bool:
        """Yazar günceller"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Authors SET Name = ?, LastName = ?, Country = ? WHERE Id = ?",
                name, lastname, country, author_id
            )
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0
        except Exception as e:
            print(f"AuthorRepository.update error: {e}")
            return False
    
    def delete(self, author_id: int) -> bool:
        """Yazar siler"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Authors WHERE Id = ?", author_id)
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0
        except Exception as e:
            print(f"AuthorRepository.delete error: {e}")
            return False

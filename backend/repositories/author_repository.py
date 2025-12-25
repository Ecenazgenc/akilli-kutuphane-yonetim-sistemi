"""
AUTHOR_REPOSITORY.PY - Yazar Veritabanı İşlemleri
"""
from typing import List, Optional
from repositories.base_repository import BaseRepository
from entities.author import Author

class AuthorRepository(BaseRepository):
    
    def get_all(self) -> List[Author]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Name, LastName, Country FROM Authors")
            return [Author(Id=row[0], Name=row[1], LastName=row[2], Country=row[3]) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[AuthorRepository.get_all] HATA: {e}")
            return []
        finally:
            if conn: conn.close()
    
    def get_by_id(self, author_id: int) -> Optional[Author]:
        if not self.validate_id(author_id):
            return None
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Name, LastName, Country FROM Authors WHERE Id = ?", (author_id,))
            row = cursor.fetchone()
            return Author(Id=row[0], Name=row[1], LastName=row[2], Country=row[3]) if row else None
        except Exception as e:
            print(f"[AuthorRepository.get_by_id] HATA: {e}")
            return None
        finally:
            if conn: conn.close()
    
    def add(self, name: str, lastname: str, country: str) -> Optional[Author]:
        if not self.validate_input(name) or not self.validate_input(lastname):
            return None
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Authors (Name, LastName, Country) VALUES (?, ?, ?); SELECT SCOPE_IDENTITY();", (name, lastname, country))
            cursor.nextset()
            new_id = cursor.fetchone()[0]
            conn.commit()
            return Author(Id=int(new_id), Name=name, LastName=lastname, Country=country)
        except Exception as e:
            print(f"[AuthorRepository.add] HATA: {e}")
            return None
        finally:
            if conn: conn.close()
    
    def update(self, author_id: int, name: str, lastname: str, country: str) -> bool:
        if not self.validate_id(author_id):
            return False
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Authors SET Name = ?, LastName = ?, Country = ? WHERE Id = ?", (name, lastname, country, author_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[AuthorRepository.update] HATA: {e}")
            return False
        finally:
            if conn: conn.close()
    
    def delete(self, author_id: int) -> bool:
        if not self.validate_id(author_id):
            return False
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Authors WHERE Id = ?", (author_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[AuthorRepository.delete] HATA: {e}")
            return False
        finally:
            if conn: conn.close()

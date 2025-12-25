"""
CATEGORY_REPOSITORY.PY - Kategori Veritabanı İşlemleri
"""
from typing import List, Optional
from repositories.base_repository import BaseRepository
from entities.category import Category

class CategoryRepository(BaseRepository):
    
    def get_all(self) -> List[Category]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Name FROM Categories")
            return [Category(Id=row[0], Name=row[1]) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[CategoryRepository.get_all] HATA: {e}")
            return []
        finally:
            if conn: conn.close()
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        if not self.validate_id(category_id):
            return None
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Name FROM Categories WHERE Id = ?", (category_id,))
            row = cursor.fetchone()
            return Category(Id=row[0], Name=row[1]) if row else None
        except Exception as e:
            print(f"[CategoryRepository.get_by_id] HATA: {e}")
            return None
        finally:
            if conn: conn.close()
    
    def add(self, name: str) -> Optional[Category]:
        if not self.validate_input(name):
            return None
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Categories (Name) VALUES (?); SELECT SCOPE_IDENTITY();", (name,))
            cursor.nextset()
            new_id = cursor.fetchone()[0]
            conn.commit()
            return Category(Id=int(new_id), Name=name)
        except Exception as e:
            print(f"[CategoryRepository.add] HATA: {e}")
            return None
        finally:
            if conn: conn.close()
    
    def update(self, category_id: int, name: str) -> bool:
        if not self.validate_id(category_id):
            return False
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Categories SET Name = ? WHERE Id = ?", (name, category_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[CategoryRepository.update] HATA: {e}")
            return False
        finally:
            if conn: conn.close()
    
    def delete(self, category_id: int) -> bool:
        if not self.validate_id(category_id):
            return False
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Categories WHERE Id = ?", (category_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[CategoryRepository.delete] HATA: {e}")
            return False
        finally:
            if conn: conn.close()

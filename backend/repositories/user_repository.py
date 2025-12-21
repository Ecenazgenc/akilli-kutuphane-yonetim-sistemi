"""
User Repository - Kullanıcı Veritabanı İşlemleri (SQL Injection Korumalı)
"""

from typing import List, Optional
from repositories.base_repository import BaseRepository
from entities.user import User


class UserRepository(BaseRepository):
    """Kullanıcı Repository - SQL Injection korumalı"""
    
    def get_all(self) -> List[User]:
        """Tüm kullanıcıları getirir"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Id, FullName, Email, PasswordHash, Role FROM Users")
            users = []
            for row in cursor.fetchall():
                users.append(User(
                    Id=row[0], FullName=row[1], Email=row[2], 
                    PasswordHash=row[3], Role=row[4]
                ))
            return users
        except Exception as e:
            print(f"[UserRepository.get_all] HATA: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """ID ile kullanıcı getirir"""
        # SQL Injection kontrolü
        if not self.validate_id(user_id, "user_id"):
            return None
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Id, FullName, Email, PasswordHash, Role FROM Users WHERE Id = ?", 
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return User(Id=row[0], FullName=row[1], Email=row[2], PasswordHash=row[3], Role=row[4])
            return None
        except Exception as e:
            print(f"[UserRepository.get_by_id] HATA: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Email ile kullanıcı getirir"""
        # SQL Injection kontrolü
        if not self.validate_email(email):
            return None
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Id, FullName, Email, PasswordHash, Role FROM Users WHERE Email = ?", 
                (email,)
            )
            row = cursor.fetchone()
            if row:
                return User(Id=row[0], FullName=row[1], Email=row[2], PasswordHash=row[3], Role=row[4])
            return None
        except Exception as e:
            print(f"[UserRepository.get_by_email] HATA: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def add(self, fullname: str, email: str, password_hash: str, role: str = "user") -> Optional[User]:
        """Yeni kullanıcı ekler"""
        # SQL Injection kontrolleri
        if not self.validate_input(fullname, "fullname"):
            print("[UserRepository.add] Geçersiz fullname")
            return None
        if not self.validate_email(email):
            print("[UserRepository.add] Geçersiz email")
            return None
        if not self.validate_input(password_hash, "password_hash"):
            print("[UserRepository.add] Geçersiz password_hash")
            return None
        if role not in ['user', 'admin']:
            print(f"[UserRepository.add] Geçersiz role: {role}")
            return None
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Users (FullName, Email, PasswordHash, Role) VALUES (?, ?, ?, ?); SELECT SCOPE_IDENTITY();",
                (fullname, email, password_hash, role)
            )
            cursor.nextset()
            new_id = cursor.fetchone()[0]
            conn.commit()
            return User(Id=int(new_id), FullName=fullname, Email=email, PasswordHash=password_hash, Role=role)
        except Exception as e:
            print(f"[UserRepository.add] HATA: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def update(self, user_id: int, fullname: str, email: str, role: str) -> bool:
        """Kullanıcı günceller"""
        # SQL Injection kontrolleri
        if not self.validate_id(user_id, "user_id"):
            return False
        if not self.validate_input(fullname, "fullname"):
            return False
        if not self.validate_email(email):
            return False
        if role not in ['user', 'admin']:
            print(f"[UserRepository.update] Geçersiz role: {role}")
            return False
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Users SET FullName = ?, Email = ?, Role = ? WHERE Id = ?",
                (fullname, email, role, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[UserRepository.update] HATA: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def delete(self, user_id: int) -> bool:
        """Kullanıcı siler"""
        if not self.validate_id(user_id, "user_id"):
            return False
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Users WHERE Id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[UserRepository.delete] HATA: {e}")
            return False
        finally:
            if conn:
                conn.close()

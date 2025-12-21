"""
User Service - Kullanıcı İş Mantığı
"""

import hashlib
from typing import List, Optional
from repositories import UserRepository
from entities import User


class UserService:
    """Kullanıcı servisi"""
    
    def __init__(self):
        self.repo = UserRepository()
    
    def get_all(self) -> List[User]:
        """Tüm kullanıcıları getirir"""
        return self.repo.get_all()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """ID ile kullanıcı getirir"""
        return self.repo.get_by_id(user_id)
    
    def create(self, fullname: str, email: str, password: str, role: str = "user") -> Optional[User]:
        """Yeni kullanıcı oluşturur"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return self.repo.add(fullname, email, password_hash, role)
    
    def update(self, user_id: int, fullname: str, email: str, role: str) -> bool:
        """Kullanıcı günceller"""
        return self.repo.update(user_id, fullname, email, role)
    
    def delete(self, user_id: int) -> bool:
        """Kullanıcı siler"""
        return self.repo.delete(user_id)


# Singleton instance
user_service = UserService()

"""USER_SERVICE.PY - Kullanıcı Servisi"""
import hashlib
from typing import List, Optional
from repositories.user_repository import UserRepository
from entities.user import User

class UserService:
    def __init__(self):
        self.repo = UserRepository()
    
    def get_all(self) -> List[User]:
        return self.repo.get_all()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.repo.get_by_id(user_id)
    
    def create(self, fullname: str, email: str, password: str, role: str = "user") -> Optional[User]:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return self.repo.add(fullname, email, password_hash, role)
    
    def update(self, user_id: int, fullname: str, email: str, role: str) -> bool:
        return self.repo.update(user_id, fullname, email, role)
    
    def delete(self, user_id: int) -> bool:
        return self.repo.delete(user_id)

user_service = UserService()

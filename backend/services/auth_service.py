"""
AUTH_SERVICE.PY - Kimlik Doğrulama Servisi
"""
import hashlib
import secrets
from typing import Optional, Tuple
from repositories.user_repository import UserRepository
from entities.user import User

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.active_sessions = {}
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_token(self, user_id: int) -> str:
        token = secrets.token_hex(32)
        self.active_sessions[token] = user_id
        return token
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        user_id = self.active_sessions.get(token)
        if user_id:
            return self.user_repo.get_by_id(user_id)
        return None
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        if not email or not password:
            return False, "Email ve şifre gerekli", None
        user = self.user_repo.get_by_email(email)
        if not user:
            return False, "Kullanıcı bulunamadı", None
        if user.PasswordHash != self.hash_password(password):
            return False, "Şifre hatalı", None
        token = self.create_token(user.Id)
        return True, token, user
    
    def register(self, fullname: str, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        if not all([fullname, email, password]):
            return False, "Tüm alanlar gerekli", None
        existing = self.user_repo.get_by_email(email)
        if existing:
            return False, "Bu email zaten kayıtlı", None
        user = self.user_repo.add(fullname, email, self.hash_password(password), "user")
        if user:
            return True, "Kayıt başarılı", user
        return False, "Kayıt başarısız", None
    
    def logout(self, token: str) -> bool:
        if token in self.active_sessions:
            del self.active_sessions[token]
            return True
        return False

auth_service = AuthService()

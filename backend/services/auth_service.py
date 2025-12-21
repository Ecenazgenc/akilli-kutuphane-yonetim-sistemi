"""
Auth Service - Kimlik Doğrulama İş Mantığı
"""

import hashlib
import secrets
from typing import Optional, Tuple
from repositories import UserRepository
from entities import User


class AuthService:
    """Kimlik doğrulama servisi"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.active_sessions = {}  # token -> user_id
    
    def hash_password(self, password: str) -> str:
        """Şifreyi hashler"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_token(self, user_id: int) -> str:
        """Oturum token'ı oluşturur"""
        token = secrets.token_hex(32)
        self.active_sessions[token] = user_id
        return token
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Token'dan kullanıcı getirir"""
        user_id = self.active_sessions.get(token)
        if user_id:
            return self.user_repo.get_by_id(user_id)
        return None
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """Kullanıcı girişi yapar"""
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
        """Yeni kullanıcı kaydı"""
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
        """Çıkış yapar"""
        if token in self.active_sessions:
            del self.active_sessions[token]
            return True
        return False


# Singleton instance
auth_service = AuthService()

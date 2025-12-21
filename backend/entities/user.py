"""
User Entity - Kullanıcı Veri Modeli
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Kullanıcı Entity"""
    Id: int
    FullName: str
    Email: str
    PasswordHash: str
    Role: str
    
    def to_dict(self) -> dict:
        """Entity'yi dictionary'e çevirir"""
        return {
            "id": self.Id,
            "fullName": self.FullName,
            "email": self.Email,
            "role": self.Role
        }
    
    def is_admin(self) -> bool:
        """Admin mi kontrol eder"""
        return self.Role == 'admin'

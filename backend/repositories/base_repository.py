"""
Base Repository - Temel veritabanı işlemleri ve SQL Injection koruması
"""

import re
from config import DatabaseConfig


class BaseRepository:
    """Temel Repository sınıfı - SQL Injection koruması içerir"""
    
    # Tehlikeli SQL kalıpları
    SQL_INJECTION_PATTERNS = [
        r"(\s|^)(DROP|TRUNCATE|ALTER|EXEC|EXECUTE)\s",
        r"--",
        r"/\*.*\*/",
        r"xp_",
        r"sp_",
        r"0x[0-9a-fA-F]{8,}",
        r";\s*(SELECT|INSERT|UPDATE|DELETE)",
    ]
    
    def get_connection(self):
        """Veritabanı bağlantısı döndürür"""
        return DatabaseConfig.get_connection()
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """String değeri temizler - tehlikeli karakterleri escape eder"""
        if value is None:
            return None
        
        if not isinstance(value, str):
            return value
        
        # Tek tırnağı escape et (SQL için)
        result = value.replace("'", "''")
        
        # Tehlikeli komutları kaldır
        dangerous_words = ["--", ";--", "/*", "*/", "xp_", "sp_", "EXEC ", "exec "]
        for word in dangerous_words:
            result = result.replace(word, "")
        
        return result.strip()
    
    @staticmethod
    def validate_input(value, field_name: str = "alan") -> bool:
        """
        Girdi değerini doğrular
        SQL Injection saldırılarına karşı kontrol eder
        """
        if value is None:
            return True
        
        if isinstance(value, (int, float)):
            return True
        
        if isinstance(value, str):
            if len(value.strip()) == 0:
                return True
            
            # Maksimum uzunluk kontrolü
            if len(value) > 1000:
                print(f"[SECURITY] {field_name} çok uzun: {len(value)} karakter")
                return False
            
            # SQL Injection pattern kontrolü
            for pattern in BaseRepository.SQL_INJECTION_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    print(f"[SECURITY] SQL Injection tespit edildi - {field_name}: {value[:50]}...")
                    return False
            
            return True
        
        return True
    
    @staticmethod
    def validate_id(value, field_name: str = "ID") -> bool:
        """ID değerini doğrular - sadece pozitif integer olmalı"""
        if value is None:
            return False
        
        try:
            int_value = int(value)
            if int_value <= 0:
                print(f"[SECURITY] Geçersiz {field_name}: {value}")
                return False
            return True
        except (ValueError, TypeError):
            print(f"[SECURITY] {field_name} integer değil: {value}")
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Email formatını doğrular"""
        if email is None:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            print(f"[SECURITY] Geçersiz email formatı: {email}")
            return False
        
        return BaseRepository.validate_input(email, "email")
    
    @staticmethod
    def validate_amount(value, field_name: str = "tutar") -> bool:
        """Para tutarını doğrular"""
        if value is None:
            return False
        
        try:
            float_value = float(value)
            if float_value < 0:
                print(f"[SECURITY] Negatif {field_name}: {value}")
                return False
            return True
        except (ValueError, TypeError):
            print(f"[SECURITY] {field_name} sayı değil: {value}")
            return False

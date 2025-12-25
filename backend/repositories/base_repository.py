"""
BASE_REPOSITORY.PY - Temel Repository Sınıfı
SQL Injection koruması ve ortak metodlar içerir.
"""
import re
from config import DatabaseConfig

class BaseRepository:
    """
    Temel Repository sınıfı.
    Tüm repository'ler bu sınıftan türetilir.
    SQL Injection koruması bu sınıfta sağlanır.
    """
    
    # SQL Injection tespiti için tehlikeli kalıplar
    SQL_INJECTION_PATTERNS = [
        r"(\s|^)(DROP|TRUNCATE|ALTER|EXEC|EXECUTE)\s",  # DDL komutları
        r"--",                    # SQL yorum satırı
        r"/\*.*\*/",             # Çok satırlı yorum
        r"xp_",                  # SQL Server extended procedures
        r"sp_",                  # System procedures (dikkatli kullan)
        r"0x[0-9a-fA-F]{8,}",    # Hex encoded strings
        r";\s*(SELECT|INSERT|UPDATE|DELETE)",  # Chained queries
        r"UNION\s+(ALL\s+)?SELECT",  # Union injection
        r"OR\s+1\s*=\s*1",      # Classic OR injection
        r"'\s*OR\s*'",          # String OR injection
    ]
    
    def get_connection(self):
        """Veritabanı bağlantısı döndürür"""
        return DatabaseConfig.get_connection()
    
    @staticmethod
    def validate_input(value, field_name: str = "alan") -> bool:
        """
        Girdi doğrulama - SQL Injection kontrolü.
        
        Args:
            value: Kontrol edilecek değer
            field_name: Hata mesajında gösterilecek alan adı
        
        Returns:
            bool: Geçerli ise True, değilse False
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
                    print(f"[SECURITY] SQL Injection tespit edildi - {field_name}: {pattern}")
                    return False
            
            return True
        
        return True
    
    @staticmethod
    def validate_id(value, field_name: str = "ID") -> bool:
        """
        ID doğrulama - Pozitif integer kontrolü.
        
        Args:
            value: Kontrol edilecek ID değeri
            field_name: Hata mesajında gösterilecek alan adı
        
        Returns:
            bool: Geçerli ise True, değilse False
        """
        if value is None:
            return False
        
        try:
            int_value = int(value)
            if int_value <= 0:
                print(f"[SECURITY] {field_name} pozitif olmalı: {int_value}")
                return False
            return True
        except (ValueError, TypeError):
            print(f"[SECURITY] {field_name} integer olmalı: {value}")
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Email doğrulama.
        
        Args:
            email: Kontrol edilecek email adresi
        
        Returns:
            bool: Geçerli ise True, değilse False
        """
        if email is None:
            return False
        
        # Email format kontrolü
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            print(f"[SECURITY] Geçersiz email formatı: {email}")
            return False
        
        # SQL Injection kontrolü
        return BaseRepository.validate_input(email, "email")
    
    @staticmethod
    def validate_amount(value, field_name: str = "tutar") -> bool:
        """
        Para tutarı doğrulama.
        
        Args:
            value: Kontrol edilecek tutar
            field_name: Hata mesajında gösterilecek alan adı
        
        Returns:
            bool: Geçerli ise True, değilse False
        """
        if value is None:
            return False
        
        try:
            float_value = float(value)
            if float_value < 0:
                print(f"[SECURITY] {field_name} negatif olamaz: {float_value}")
                return False
            return True
        except (ValueError, TypeError):
            print(f"[SECURITY] {field_name} sayı olmalı: {value}")
            return False

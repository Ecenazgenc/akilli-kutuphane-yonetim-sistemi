"""
CONFIG.PY - Veritabanı Konfigürasyonu
"""
import pyodbc

class DatabaseConfig:
    SERVER = r'excaliburG870\SQLEXPRESS'
    DATABASE = 'KutuphaneDB'
    DRIVER = '{ODBC Driver 17 for SQL Server}'
    
    @classmethod
    def get_connection_string(cls):
        return f'DRIVER={cls.DRIVER};SERVER={cls.SERVER};DATABASE={cls.DATABASE};Trusted_Connection=yes;'
    
    @classmethod
    def get_connection(cls):
        return pyodbc.connect(cls.get_connection_string())
    
    @classmethod
    def test_connection(cls):
        try:
            conn = cls.get_connection()
            conn.close()
            return True, "Bağlantı başarılı"
        except Exception as e:
            return False, str(e)

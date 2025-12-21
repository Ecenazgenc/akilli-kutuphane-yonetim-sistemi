"""
Penalty Repository - Ceza Veritabanı İşlemleri (SQL Injection Korumalı)
"""

from typing import List, Optional
from datetime import datetime
from repositories.base_repository import BaseRepository
from entities.penalty import Penalty


class PenaltyRepository(BaseRepository):
    """Ceza Repository - SQL Injection korumalı"""
    
    def get_all(self) -> List[Penalty]:
        """Tüm cezaları getirir"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql = """
                SELECT 
                    p.Id, 
                    p.Amount, 
                    p.BorrowTransactionsId, 
                    p.NumberOfDay,
                    u.FullName,
                    bt.UserId
                FROM Penalties p
                INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
                INNER JOIN Users u ON bt.UserId = u.Id
                ORDER BY p.Id DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            penalties = []
            for row in rows:
                penalty = Penalty(
                    Id=row[0],
                    Amount=float(row[1]) if row[1] else 0.0,
                    BorrowTransactionsId=row[2],
                    NumberOfDay=row[3] if row[3] else 0,
                    Date=datetime.now(),
                    UserName=row[4] if row[4] else "Bilinmiyor",
                    UserId=row[5] if row[5] else 0
                )
                penalties.append(penalty)
            
            print(f"[PenaltyRepository.get_all] {len(penalties)} ceza bulundu")
            return penalties
            
        except Exception as e:
            print(f"[PenaltyRepository.get_all] HATA: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_by_id(self, penalty_id: int) -> Optional[Penalty]:
        """ID ile ceza getirir"""
        # SQL Injection kontrolü
        if not self.validate_id(penalty_id, "penalty_id"):
            return None
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql = """
                SELECT 
                    p.Id, 
                    p.Amount, 
                    p.BorrowTransactionsId, 
                    p.NumberOfDay,
                    u.FullName,
                    bt.UserId
                FROM Penalties p
                INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
                INNER JOIN Users u ON bt.UserId = u.Id
                WHERE p.Id = ?
            """
            cursor.execute(sql, (penalty_id,))
            row = cursor.fetchone()
            
            if row:
                return Penalty(
                    Id=row[0],
                    Amount=float(row[1]) if row[1] else 0.0,
                    BorrowTransactionsId=row[2],
                    NumberOfDay=row[3] if row[3] else 0,
                    Date=datetime.now(),
                    UserName=row[4] if row[4] else "Bilinmiyor",
                    UserId=row[5] if row[5] else 0
                )
            return None
            
        except Exception as e:
            print(f"[PenaltyRepository.get_by_id] HATA: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_by_user_id(self, user_id: int) -> List[Penalty]:
        """Kullanıcının cezalarını getirir"""
        # SQL Injection kontrolü
        if not self.validate_id(user_id, "user_id"):
            return []
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql = """
                SELECT 
                    p.Id, 
                    p.Amount, 
                    p.BorrowTransactionsId, 
                    p.NumberOfDay,
                    u.FullName,
                    bt.UserId
                FROM Penalties p
                INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
                INNER JOIN Users u ON bt.UserId = u.Id
                WHERE bt.UserId = ?
                ORDER BY p.Id DESC
            """
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
            
            penalties = []
            for row in rows:
                penalty = Penalty(
                    Id=row[0],
                    Amount=float(row[1]) if row[1] else 0.0,
                    BorrowTransactionsId=row[2],
                    NumberOfDay=row[3] if row[3] else 0,
                    Date=datetime.now(),
                    UserName=row[4] if row[4] else "Bilinmiyor",
                    UserId=row[5] if row[5] else 0
                )
                penalties.append(penalty)
            
            print(f"[PenaltyRepository.get_by_user_id] User {user_id}: {len(penalties)} ceza")
            return penalties
            
        except Exception as e:
            print(f"[PenaltyRepository.get_by_user_id] HATA: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def add(self, borrow_tx_id: int, delay_minutes: int, amount: float) -> Optional[Penalty]:
        """Yeni ceza ekler"""
        # SQL Injection kontrolleri
        if not self.validate_id(borrow_tx_id, "borrow_tx_id"):
            print("[PenaltyRepository.add] Geçersiz borrow_tx_id")
            return None
        if not self.validate_id(delay_minutes, "delay_minutes"):
            print("[PenaltyRepository.add] Geçersiz delay_minutes")
            return None
        if not self.validate_amount(amount, "amount"):
            print("[PenaltyRepository.add] Geçersiz amount")
            return None
        
        conn = None
        try:
            print(f"[PenaltyRepository.add] Ceza ekleniyor: tx={borrow_tx_id}, dakika={delay_minutes}, tutar={amount}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Transaction kontrolü
            cursor.execute("SELECT Id, UserId FROM BorrowTransactions WHERE Id = ?", (borrow_tx_id,))
            tx_row = cursor.fetchone()
            
            if not tx_row:
                print(f"[PenaltyRepository.add] Transaction bulunamadı: {borrow_tx_id}")
                return None
            
            print(f"[PenaltyRepository.add] Transaction OK: Id={tx_row[0]}, UserId={tx_row[1]}")
            
            # Ceza ekle
            cursor.execute(
                "INSERT INTO Penalties (BorrowTransactionsId, NumberOfDay, Amount) VALUES (?, ?, ?)",
                (borrow_tx_id, delay_minutes, amount)
            )
            conn.commit()
            
            # Yeni ID al
            cursor.execute("SELECT @@IDENTITY")
            new_id_row = cursor.fetchone()
            
            if new_id_row and new_id_row[0]:
                new_id = int(new_id_row[0])
                print(f"[PenaltyRepository.add] ✓ Ceza eklendi: ID={new_id}")
                return self.get_by_id(new_id)
            
            print("[PenaltyRepository.add] ID alınamadı")
            return None
            
        except Exception as e:
            print(f"[PenaltyRepository.add] HATA: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if conn:
                conn.close()
    
    def delete(self, penalty_id: int) -> bool:
        """Ceza siler"""
        if not self.validate_id(penalty_id, "penalty_id"):
            return False
        
        conn = None
        try:
            print(f"[PenaltyRepository.delete] Ceza siliniyor: {penalty_id}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Penalties WHERE Id = ?", (penalty_id,))
            conn.commit()
            
            deleted = cursor.rowcount > 0
            print(f"[PenaltyRepository.delete] Silindi: {deleted}")
            return deleted
            
        except Exception as e:
            print(f"[PenaltyRepository.delete] HATA: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_total_amount(self) -> float:
        """Toplam ceza tutarı"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ISNULL(SUM(p.Amount), 0) 
                FROM Penalties p
                INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
            """)
            row = cursor.fetchone()
            return float(row[0]) if row and row[0] else 0.0
        except Exception as e:
            print(f"[PenaltyRepository.get_total_amount] HATA: {e}")
            return 0.0
        finally:
            if conn:
                conn.close()
    
    def get_user_total_amount(self, user_id: int) -> float:
        """Kullanıcının toplam ceza tutarı"""
        if not self.validate_id(user_id, "user_id"):
            return 0.0
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ISNULL(SUM(p.Amount), 0) 
                FROM Penalties p
                INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
                WHERE bt.UserId = ?
            """, (user_id,))
            row = cursor.fetchone()
            total = float(row[0]) if row and row[0] else 0.0
            print(f"[PenaltyRepository.get_user_total_amount] User {user_id}: {total} TL")
            return total
        except Exception as e:
            print(f"[PenaltyRepository.get_user_total_amount] HATA: {e}")
            return 0.0
        finally:
            if conn:
                conn.close()
    
    def user_has_unpaid_penalty(self, user_id: int) -> bool:
        """Kullanıcının ödenmemiş cezası var mı?"""
        if not self.validate_id(user_id, "user_id"):
            return False
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM Penalties p
                INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
                WHERE bt.UserId = ?
            """, (user_id,))
            row = cursor.fetchone()
            count = row[0] if row else 0
            return count > 0
        except Exception as e:
            print(f"[PenaltyRepository.user_has_unpaid_penalty] HATA: {e}")
            return False
        finally:
            if conn:
                conn.close()

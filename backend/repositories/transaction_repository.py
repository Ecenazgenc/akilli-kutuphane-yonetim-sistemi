"""
Transaction Repository - Ödünç İşlemi Veritabanı İşlemleri (SQL Injection Korumalı)
"""

from typing import List, Optional
from datetime import datetime
from repositories.base_repository import BaseRepository
from entities.borrow_transaction import BorrowTransaction


class TransactionRepository(BaseRepository):
    """Ödünç İşlemi Repository - SQL Injection korumalı"""
    
    def get_all(self) -> List[BorrowTransaction]:
        """Tüm işlemleri getirir"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bt.Id, bt.BookId, bt.UserId, bt.BorrowDate, bt.ReturnDate, bt.RealReturnDate,
                       ISNULL(b.Title, '') AS BookTitle, ISNULL(u.FullName, '') AS UserName
                FROM BorrowTransactions bt
                LEFT JOIN Books b ON bt.BookId = b.Id
                LEFT JOIN Users u ON bt.UserId = u.Id
                ORDER BY bt.BorrowDate DESC
            """)
            transactions = []
            for row in cursor.fetchall():
                transactions.append(BorrowTransaction(
                    Id=row[0], BookId=row[1], UserId=row[2],
                    BorrowDate=row[3], ReturnDate=row[4], RealReturnDate=row[5],
                    BookTitle=row[6], UserName=row[7]
                ))
            return transactions
        except Exception as e:
            print(f"[TransactionRepository.get_all] HATA: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_by_id(self, tx_id: int) -> Optional[BorrowTransaction]:
        """ID ile işlem getirir"""
        if not self.validate_id(tx_id, "tx_id"):
            return None
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bt.Id, bt.BookId, bt.UserId, bt.BorrowDate, bt.ReturnDate, bt.RealReturnDate,
                       ISNULL(b.Title, '') AS BookTitle, ISNULL(u.FullName, '') AS UserName
                FROM BorrowTransactions bt
                LEFT JOIN Books b ON bt.BookId = b.Id
                LEFT JOIN Users u ON bt.UserId = u.Id
                WHERE bt.Id = ?
            """, (tx_id,))
            row = cursor.fetchone()
            if row:
                return BorrowTransaction(
                    Id=row[0], BookId=row[1], UserId=row[2],
                    BorrowDate=row[3], ReturnDate=row[4], RealReturnDate=row[5],
                    BookTitle=row[6], UserName=row[7]
                )
            return None
        except Exception as e:
            print(f"[TransactionRepository.get_by_id] HATA: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_by_user_id(self, user_id: int) -> List[BorrowTransaction]:
        """Kullanıcının işlemlerini getirir"""
        if not self.validate_id(user_id, "user_id"):
            return []
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bt.Id, bt.BookId, bt.UserId, bt.BorrowDate, bt.ReturnDate, bt.RealReturnDate,
                       ISNULL(b.Title, '') AS BookTitle, ISNULL(u.FullName, '') AS UserName
                FROM BorrowTransactions bt
                LEFT JOIN Books b ON bt.BookId = b.Id
                LEFT JOIN Users u ON bt.UserId = u.Id
                WHERE bt.UserId = ?
                ORDER BY bt.BorrowDate DESC
            """, (user_id,))
            transactions = []
            for row in cursor.fetchall():
                transactions.append(BorrowTransaction(
                    Id=row[0], BookId=row[1], UserId=row[2],
                    BorrowDate=row[3], ReturnDate=row[4], RealReturnDate=row[5],
                    BookTitle=row[6], UserName=row[7]
                ))
            return transactions
        except Exception as e:
            print(f"[TransactionRepository.get_by_user_id] HATA: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def add(self, book_id: int, user_id: int, borrow_date: datetime, return_date: datetime) -> Optional[BorrowTransaction]:
        """Yeni işlem ekler"""
        if not self.validate_id(book_id, "book_id"):
            return None
        if not self.validate_id(user_id, "user_id"):
            return None
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO BorrowTransactions (BookId, UserId, BorrowDate, ReturnDate) 
                VALUES (?, ?, ?, ?); 
                SELECT SCOPE_IDENTITY();
            """, (book_id, user_id, borrow_date, return_date))
            cursor.nextset()
            new_id = cursor.fetchone()[0]
            conn.commit()
            print(f"[TransactionRepository.add] İşlem eklendi: id={new_id}")
            return self.get_by_id(int(new_id))
        except Exception as e:
            print(f"[TransactionRepository.add] HATA: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def update_return(self, tx_id: int, real_return_date: datetime) -> Optional[BorrowTransaction]:
        """İade tarihini günceller"""
        if not self.validate_id(tx_id, "tx_id"):
            return None
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE BorrowTransactions SET RealReturnDate = ? WHERE Id = ?", 
                (real_return_date, tx_id)
            )
            conn.commit()
            print(f"[TransactionRepository.update_return] İade kaydedildi: tx_id={tx_id}")
            return self.get_by_id(tx_id)
        except Exception as e:
            print(f"[TransactionRepository.update_return] HATA: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def delete(self, tx_id: int) -> bool:
        """İşlem siler"""
        if not self.validate_id(tx_id, "tx_id"):
            return False
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Penalties WHERE BorrowTransactionsId = ?", (tx_id,))
            cursor.execute("DELETE FROM BorrowTransactions WHERE Id = ?", (tx_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[TransactionRepository.delete] HATA: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def count_active_by_user(self, user_id: int) -> int:
        """Kullanıcının aktif ödünç sayısı"""
        if not self.validate_id(user_id, "user_id"):
            return 0
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM BorrowTransactions WHERE UserId = ? AND RealReturnDate IS NULL",
                (user_id,)
            )
            count = cursor.fetchone()[0]
            return count or 0
        except Exception as e:
            print(f"[TransactionRepository.count_active_by_user] HATA: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    def has_active_borrow(self, user_id: int, book_id: int) -> bool:
        """Kullanıcı bu kitabı ödünç almış mı?"""
        if not self.validate_id(user_id, "user_id"):
            return False
        if not self.validate_id(book_id, "book_id"):
            return False
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM BorrowTransactions WHERE UserId = ? AND BookId = ? AND RealReturnDate IS NULL",
                (user_id, book_id)
            )
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"[TransactionRepository.has_active_borrow] HATA: {e}")
            return False
        finally:
            if conn:
                conn.close()

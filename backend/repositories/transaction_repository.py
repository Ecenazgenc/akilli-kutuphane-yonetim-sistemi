"""
TRANSACTION_REPOSITORY.PY - Ödünç İşlemi Veritabanı İşlemleri

*** STORED PROCEDURE KULLANIR ***
- sp_BorrowBook: Kitap ödünç alma
- sp_ReturnBook: Kitap iade etme (Trigger otomatik ceza hesaplar)
"""
from typing import List, Optional, Tuple
from repositories.base_repository import BaseRepository
from entities.borrow_transaction import BorrowTransaction

class TransactionRepository(BaseRepository):
    
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
            if conn: conn.close()
    
    def get_by_id(self, tx_id: int) -> Optional[BorrowTransaction]:
        """ID ile işlem getirir"""
        if not self.validate_id(tx_id):
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
            if conn: conn.close()
    
    def get_by_user_id(self, user_id: int) -> List[BorrowTransaction]:
        """Kullanıcının işlemlerini getirir"""
        if not self.validate_id(user_id):
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
            if conn: conn.close()
    
    def borrow_book_sp(self, book_id: int, user_id: int) -> Tuple[bool, str, Optional[int]]:
        """
        STORED PROCEDURE ile kitap ödünç alma: sp_BorrowBook
        
        Returns:
            Tuple[bool, str, Optional[int]]: (başarı, mesaj, yeni_işlem_id)
        """
        if not self.validate_id(book_id) or not self.validate_id(user_id):
            return False, "Geçersiz parametreler", None
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Stored Procedure çağır - SET NOCOUNT ON ile
            sql = """
                SET NOCOUNT ON;
                DECLARE @NewId INT, @ErrMsg NVARCHAR(500);
                EXEC sp_BorrowBook 
                    @BookId = ?, 
                    @UserId = ?, 
                    @LoanDurationMinutes = 1,
                    @NewTransactionId = @NewId OUTPUT, 
                    @ErrorMessage = @ErrMsg OUTPUT;
                SELECT @NewId AS NewId, @ErrMsg AS ErrorMsg;
            """
            cursor.execute(sql, (book_id, user_id))
            
            # Tüm result set'leri atla ve son SELECT'e ulaş
            while cursor.description is None:
                if not cursor.nextset():
                    break
            
            row = cursor.fetchone()
            conn.commit()
            
            if row:
                new_id = row[0]
                error_msg = row[1]
                
                if new_id and new_id > 0:
                    tx = self.get_by_id(new_id)
                    if tx:
                        return_date_str = tx.ReturnDate.strftime('%d.%m.%Y %H:%M:%S')
                        return True, f"'{tx.BookTitle}' kitabı ödünç alındı. Son iade: {return_date_str}", new_id
                    return True, "Kitap ödünç alındı", new_id
                else:
                    return False, error_msg if error_msg else "İşlem başarısız", None
            
            return False, "Bilinmeyen hata", None
            
        except Exception as e:
            print(f"[TransactionRepository.borrow_book_sp] HATA: {e}")
            return False, str(e), None
        finally:
            if conn: conn.close()
    
    def return_book_sp(self, tx_id: int, user_id: int) -> Tuple[bool, str]:
        """
        STORED PROCEDURE ile kitap iade: sp_ReturnBook
        TRIGGER (trg_CalculatePenalty) otomatik olarak ceza hesaplar!
        
        Returns:
            Tuple[bool, str]: (başarı, mesaj)
        """
        if not self.validate_id(tx_id) or not self.validate_id(user_id):
            return False, "Geçersiz parametreler"
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql = """
                SET NOCOUNT ON;
                DECLARE @Suc BIT, @Msg NVARCHAR(500);
                EXEC sp_ReturnBook 
                    @TransactionId = ?, 
                    @UserId = ?,
                    @Success = @Suc OUTPUT, 
                    @Message = @Msg OUTPUT;
                SELECT @Suc AS Success, @Msg AS Message;
            """
            cursor.execute(sql, (tx_id, user_id))
            
            while cursor.description is None:
                if not cursor.nextset():
                    break
            
            row = cursor.fetchone()
            conn.commit()
            
            if row:
                success = bool(row[0]) if row[0] is not None else False
                message = row[1] if row[1] else "İşlem tamamlandı"
                return success, message
            
            return False, "Bilinmeyen hata"
            
        except Exception as e:
            print(f"[TransactionRepository.return_book_sp] HATA: {e}")
            return False, str(e)
        finally:
            if conn: conn.close()
    
    def delete(self, tx_id: int) -> bool:
        """İşlem siler"""
        if not self.validate_id(tx_id):
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
            if conn: conn.close()
    
    def count_active_by_user(self, user_id: int) -> int:
        """Kullanıcının aktif ödünç sayısı"""
        if not self.validate_id(user_id):
            return 0
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM BorrowTransactions WHERE UserId = ? AND RealReturnDate IS NULL", (user_id,))
            return cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"[TransactionRepository.count_active_by_user] HATA: {e}")
            return 0
        finally:
            if conn: conn.close()

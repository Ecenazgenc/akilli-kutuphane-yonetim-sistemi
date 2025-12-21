"""
Borrow Service - Ödünç Alma İş Mantığı
"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from repositories.transaction_repository import TransactionRepository
from repositories.book_repository import BookRepository
from repositories.penalty_repository import PenaltyRepository
from entities.borrow_transaction import BorrowTransaction


class BorrowService:
    """Ödünç Alma Service Sınıfı"""
    
    # Ayarlar
    LOAN_DURATION_MINUTES = 1      # Test için 1 dakika
    PENALTY_PER_MINUTE = 5.0       # Dakika başına 5 TL ceza
    
    def __init__(self):
        self.tx_repo = TransactionRepository()
        self.book_repo = BookRepository()
        self.penalty_repo = PenaltyRepository()
    
    def get_all_transactions(self) -> List[BorrowTransaction]:
        """Tüm işlemleri getirir"""
        return self.tx_repo.get_all()
    
    def get_user_transactions(self, user_id: int) -> List[BorrowTransaction]:
        """Kullanıcının işlemlerini getirir"""
        return self.tx_repo.get_by_user_id(user_id)
    
    def get_transaction_by_id(self, tx_id: int) -> Optional[BorrowTransaction]:
        """ID ile işlem getirir"""
        return self.tx_repo.get_by_id(tx_id)
    
    def borrow_book(self, user_id: int, book_id: int) -> Tuple[bool, str, Optional[BorrowTransaction]]:
        """Kitap ödünç alma işlemi"""
        print(f"[BorrowService.borrow_book] User {user_id} kitap {book_id} ödünç almak istiyor")
        
        # Kitap var mı?
        book = self.book_repo.get_by_id(book_id)
        if not book:
            return False, "Kitap bulunamadı", None
        
        # Stokta var mı?
        if not book.is_available():
            return False, "Kitap stokta yok", None
        
        # Aynı kitabı zaten ödünç almış mı?
        if self.tx_repo.has_active_borrow(user_id, book_id):
            return False, "Bu kitabı zaten ödünç almışsınız", None
        
        # Ödenmemiş ceza var mı?
        if self.penalty_repo.user_has_unpaid_penalty(user_id):
            return False, "Ödenmemiş cezanız var. Önce cezanızı ödeyin.", None
        
        # Tarihleri hesapla
        borrow_date = datetime.now()
        return_date = borrow_date + timedelta(minutes=self.LOAN_DURATION_MINUTES)
        
        print(f"[BorrowService.borrow_book] Ödünç: {borrow_date}, İade: {return_date}")
        
        # İşlem oluştur
        tx = self.tx_repo.add(book_id, user_id, borrow_date, return_date)
        if tx:
            msg = f"'{book.Title}' kitabı ödünç alındı. Son iade tarihi: {return_date.strftime('%d.%m.%Y %H:%M:%S')}"
            print(f"[BorrowService.borrow_book] Başarılı: {msg}")
            return True, msg, tx
        
        return False, "İşlem oluşturulamadı", None
    
    def return_book(self, tx_id: int, user_id: int) -> Tuple[bool, str, Optional[BorrowTransaction]]:
        """Kitap iade işlemi - CEZA HESAPLAMA BURADA"""
        print(f"[BorrowService.return_book] ========== İADE İŞLEMİ BAŞLADI ==========")
        print(f"[BorrowService.return_book] Transaction ID: {tx_id}, User ID: {user_id}")
        
        # İşlemi getir
        tx = self.tx_repo.get_by_id(tx_id)
        if not tx:
            print(f"[BorrowService.return_book] HATA: İşlem bulunamadı")
            return False, "İşlem bulunamadı", None
        
        print(f"[BorrowService.return_book] İşlem bulundu: BookId={tx.BookId}, UserId={tx.UserId}")
        print(f"[BorrowService.return_book] BorrowDate: {tx.BorrowDate}")
        print(f"[BorrowService.return_book] ReturnDate (son tarih): {tx.ReturnDate}")
        print(f"[BorrowService.return_book] RealReturnDate: {tx.RealReturnDate}")
        
        # Bu işlem bu kullanıcıya mı ait?
        if tx.UserId != user_id:
            print(f"[BorrowService.return_book] HATA: İşlem başka kullanıcıya ait")
            return False, "Bu işlem size ait değil", None
        
        # Zaten iade edilmiş mi?
        if tx.RealReturnDate is not None:
            print(f"[BorrowService.return_book] HATA: Zaten iade edilmiş")
            return False, "Kitap zaten iade edilmiş", None
        
        # Şu anki zaman
        real_return_date = datetime.now()
        print(f"[BorrowService.return_book] Gerçek iade zamanı: {real_return_date}")
        
        # İade işlemini kaydet
        updated_tx = self.tx_repo.update_return(tx_id, real_return_date)
        if not updated_tx:
            print(f"[BorrowService.return_book] HATA: İade güncellenemedi")
            return False, "İade işlemi başarısız", None
        
        print(f"[BorrowService.return_book] İade kaydedildi")
        
        # ========== GECİKME KONTROLÜ ==========
        print(f"[BorrowService.return_book] ========== GECİKME KONTROLÜ ==========")
        print(f"[BorrowService.return_book] Son iade tarihi: {tx.ReturnDate}")
        print(f"[BorrowService.return_book] Gerçek iade tarihi: {real_return_date}")
        
        # Gecikme var mı?
        if real_return_date > tx.ReturnDate:
            print(f"[BorrowService.return_book] !!! GECİKME TESPİT EDİLDİ !!!")
            
            # Gecikme süresini hesapla (saniye cinsinden)
            delay_timedelta = real_return_date - tx.ReturnDate
            delay_seconds = delay_timedelta.total_seconds()
            print(f"[BorrowService.return_book] Gecikme süresi: {delay_seconds} saniye")
            
            # Dakikaya çevir (en az 1 dakika)
            delay_minutes = int(delay_seconds / 60)
            if delay_minutes < 1:
                delay_minutes = 1
            print(f"[BorrowService.return_book] Gecikme dakika: {delay_minutes}")
            
            # Ceza tutarını hesapla
            penalty_amount = delay_minutes * self.PENALTY_PER_MINUTE
            print(f"[BorrowService.return_book] Ceza tutarı: {delay_minutes} x {self.PENALTY_PER_MINUTE} = {penalty_amount} TL")
            
            # ========== CEZA EKLE ==========
            print(f"[BorrowService.return_book] Ceza ekleniyor...")
            penalty = self.penalty_repo.add(tx_id, delay_minutes, penalty_amount)
            
            if penalty:
                print(f"[BorrowService.return_book] ✓ CEZA EKLENDİ: ID={penalty.Id}, Tutar={penalty.Amount} TL")
                msg = f"Kitap iade edildi. {delay_minutes} dakika gecikme için {penalty_amount:.2f} TL ceza kesildi!"
                return True, msg, updated_tx
            else:
                print(f"[BorrowService.return_book] ✗ CEZA EKLENEMEDİ!")
                # Ceza eklenemese bile iade başarılı sayılır
                msg = f"Kitap iade edildi ancak ceza kaydedilemedi. Lütfen yöneticiyle iletişime geçin."
                return True, msg, updated_tx
        else:
            print(f"[BorrowService.return_book] Gecikme yok, zamanında iade edildi")
            return True, "Kitap başarıyla iade edildi. Teşekkürler!", updated_tx
    
    def create_transaction_for_admin(self, book_id: int, user_id: int) -> Tuple[bool, str, Optional[BorrowTransaction]]:
        """Admin için işlem oluşturur"""
        book = self.book_repo.get_by_id(book_id)
        if not book:
            return False, "Kitap bulunamadı", None
        
        if not book.is_available():
            return False, "Kitap stokta yok", None
        
        borrow_date = datetime.now()
        return_date = borrow_date + timedelta(minutes=self.LOAN_DURATION_MINUTES)
        
        tx = self.tx_repo.add(book_id, user_id, borrow_date, return_date)
        if tx:
            return True, "İşlem oluşturuldu", tx
        return False, "İşlem oluşturulamadı", None
    
    def delete_transaction(self, tx_id: int) -> bool:
        """İşlem siler"""
        return self.tx_repo.delete(tx_id)


# Singleton instance
borrow_service = BorrowService()

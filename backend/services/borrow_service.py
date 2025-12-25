"""
BORROW_SERVICE.PY - Ödünç Alma Servisi

*** STORED PROCEDURE ve TRIGGER KULLANIR ***
- sp_BorrowBook: Kitap ödünç alma
- sp_ReturnBook: Kitap iade etme
- trg_CalculatePenalty: Gecikme cezası otomatik hesaplama

CEZA SİSTEMİ:
- İade süresi: 1 dakika
- Gecikme cezası: 5 TL/dakika (SQL Trigger'da hesaplanır)
"""
from typing import List, Optional, Tuple
from repositories.transaction_repository import TransactionRepository
from entities.borrow_transaction import BorrowTransaction

class BorrowService:
    def __init__(self):
        self.tx_repo = TransactionRepository()
    
    def get_all_transactions(self) -> List[BorrowTransaction]:
        return self.tx_repo.get_all()
    
    def get_user_transactions(self, user_id: int) -> List[BorrowTransaction]:
        return self.tx_repo.get_by_user_id(user_id)
    
    def get_transaction_by_id(self, tx_id: int) -> Optional[BorrowTransaction]:
        return self.tx_repo.get_by_id(tx_id)
    
    def borrow_book(self, user_id: int, book_id: int) -> Tuple[bool, str, Optional[BorrowTransaction]]:
        """Kitap ödünç alma - sp_BorrowBook STORED PROCEDURE kullanır"""
        success, message, new_id = self.tx_repo.borrow_book_sp(book_id, user_id)
        if success and new_id:
            tx = self.tx_repo.get_by_id(new_id)
            return True, message, tx
        return False, message, None
    
    def return_book(self, tx_id: int, user_id: int) -> Tuple[bool, str, Optional[BorrowTransaction]]:
        """Kitap iade - sp_ReturnBook + trg_CalculatePenalty kullanır"""
        success, message = self.tx_repo.return_book_sp(tx_id, user_id)
        if success:
            tx = self.tx_repo.get_by_id(tx_id)
            return True, message, tx
        return False, message, None
    
    def delete_transaction(self, tx_id: int) -> bool:
        return self.tx_repo.delete(tx_id)

borrow_service = BorrowService()

"""
Penalty Service - Ceza İş Mantığı
"""

from typing import List, Optional, Tuple
from repositories.penalty_repository import PenaltyRepository
from entities.penalty import Penalty


class PenaltyService:
    """Ceza Service Sınıfı - İş Mantığı Katmanı"""
    
    def __init__(self):
        self.repository = PenaltyRepository()
    
    def get_all_penalties(self) -> List[Penalty]:
        """Tüm cezaları getirir"""
        print("[PenaltyService.get_all_penalties] Tüm cezalar getiriliyor...")
        penalties = self.repository.get_all()
        print(f"[PenaltyService.get_all_penalties] {len(penalties)} ceza döndürülüyor")
        return penalties
    
    def get_penalty_by_id(self, penalty_id: int) -> Optional[Penalty]:
        """ID ile ceza getirir"""
        print(f"[PenaltyService.get_penalty_by_id] Ceza getiriliyor: {penalty_id}")
        return self.repository.get_by_id(penalty_id)
    
    def get_user_penalties(self, user_id: int) -> List[Penalty]:
        """Kullanıcının cezalarını getirir"""
        print(f"[PenaltyService.get_user_penalties] User {user_id} cezaları getiriliyor...")
        penalties = self.repository.get_by_user_id(user_id)
        print(f"[PenaltyService.get_user_penalties] {len(penalties)} ceza döndürülüyor")
        return penalties
    
    def create_penalty(self, borrow_tx_id: int, delay_minutes: int, amount: float) -> Optional[Penalty]:
        """Yeni ceza oluşturur"""
        print(f"[PenaltyService.create_penalty] Ceza oluşturuluyor: tx={borrow_tx_id}, dakika={delay_minutes}, tutar={amount}")
        penalty = self.repository.add(borrow_tx_id, delay_minutes, amount)
        if penalty:
            print(f"[PenaltyService.create_penalty] Ceza oluşturuldu: ID={penalty.Id}")
        else:
            print(f"[PenaltyService.create_penalty] Ceza oluşturulamadı!")
        return penalty
    
    def pay_penalty(self, penalty_id: int, user_id: int) -> Tuple[bool, str]:
        """Ceza öder (siler)"""
        print(f"[PenaltyService.pay_penalty] Ceza ödeniyor: penalty_id={penalty_id}, user_id={user_id}")
        
        # Cezayı getir
        penalty = self.repository.get_by_id(penalty_id)
        if not penalty:
            print(f"[PenaltyService.pay_penalty] Ceza bulunamadı: {penalty_id}")
            return False, "Ceza bulunamadı"
        
        # Ceza bu kullanıcıya mı ait?
        if penalty.UserId != user_id:
            print(f"[PenaltyService.pay_penalty] Ceza başka kullanıcıya ait: {penalty.UserId} != {user_id}")
            return False, "Bu ceza size ait değil"
        
        # Cezayı sil
        amount = penalty.Amount
        if self.repository.delete(penalty_id):
            print(f"[PenaltyService.pay_penalty] Ceza ödendi: {amount} TL")
            return True, f"{amount:.2f} TL ceza başarıyla ödendi"
        
        print(f"[PenaltyService.pay_penalty] Ödeme başarısız!")
        return False, "Ödeme işlemi başarısız"
    
    def delete_penalty(self, penalty_id: int) -> bool:
        """Ceza siler (admin)"""
        print(f"[PenaltyService.delete_penalty] Ceza siliniyor: {penalty_id}")
        return self.repository.delete(penalty_id)
    
    def get_total_penalty_amount(self) -> float:
        """Toplam ceza tutarını döndürür"""
        return self.repository.get_total_amount()
    
    def get_user_total_penalty(self, user_id: int) -> float:
        """Kullanıcının toplam ceza tutarını döndürür"""
        return self.repository.get_user_total_amount(user_id)
    
    def user_has_unpaid_penalty(self, user_id: int) -> bool:
        """Kullanıcının ödenmemiş cezası var mı?"""
        return self.repository.user_has_unpaid_penalty(user_id)


# Singleton instance
penalty_service = PenaltyService()

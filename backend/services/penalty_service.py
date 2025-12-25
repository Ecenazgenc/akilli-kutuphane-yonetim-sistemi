"""
PENALTY_SERVICE.PY - Ceza Servisi
Cezalar TRIGGER tarafından otomatik oluşturulur!
"""
from typing import List, Optional, Tuple
from repositories.penalty_repository import PenaltyRepository
from entities.penalty import Penalty

class PenaltyService:
    def __init__(self):
        self.repo = PenaltyRepository()
    
    def get_all_penalties(self) -> List[Penalty]:
        return self.repo.get_all()
    
    def get_penalty_by_id(self, penalty_id: int) -> Optional[Penalty]:
        return self.repo.get_by_id(penalty_id)
    
    def get_user_penalties(self, user_id: int) -> List[Penalty]:
        return self.repo.get_by_user_id(user_id)
    
    def pay_penalty(self, penalty_id: int, user_id: int) -> Tuple[bool, str]:
        """Ceza ödeme - sp_PayPenalty kullanır"""
        return self.repo.pay_penalty_sp(penalty_id, user_id)
    
    def delete_penalty(self, penalty_id: int) -> bool:
        return self.repo.delete(penalty_id)
    
    def get_total_penalty_amount(self) -> float:
        return self.repo.get_total_amount()
    
    def get_user_total_penalty(self, user_id: int) -> float:
        return self.repo.get_user_total_amount(user_id)

penalty_service = PenaltyService()

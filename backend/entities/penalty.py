"""
Penalty Entity - Ceza Veri Modeli
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Penalty:
    """Ceza Entity Sınıfı"""
    Id: int
    Amount: float
    BorrowTransactionsId: int
    NumberOfDay: int
    Date: Optional[datetime]
    UserName: Optional[str] = None
    UserId: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Entity'yi JSON formatına çevirir"""
        date_str = ""
        if self.Date:
            date_str = self.Date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        return {
            "id": self.Id,
            "amount": float(self.Amount) if self.Amount else 0.0,
            "borrowTransactionsId": self.BorrowTransactionsId,
            "numberOfDay": self.NumberOfDay if self.NumberOfDay else 0,
            "date": date_str,
            "userName": self.UserName if self.UserName else "Bilinmiyor",
            "userId": self.UserId if self.UserId else 0
        }

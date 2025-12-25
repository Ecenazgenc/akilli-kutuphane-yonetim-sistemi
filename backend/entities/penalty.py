from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Penalty:
    Id: int
    Amount: float
    BorrowTransactionsId: int
    NumberOfDay: int
    Date: Optional[datetime] = None
    UserName: Optional[str] = None
    UserId: Optional[int] = None
    
    def to_dict(self) -> dict:
        date_str = self.Date.strftime("%Y-%m-%d %H:%M:%S") if self.Date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "id": self.Id,
            "amount": float(self.Amount) if self.Amount else 0.0,
            "borrowTransactionsId": self.BorrowTransactionsId,
            "numberOfDay": self.NumberOfDay if self.NumberOfDay else 0,
            "date": date_str,
            "userName": self.UserName if self.UserName else "Bilinmiyor",
            "userId": self.UserId if self.UserId else 0
        }

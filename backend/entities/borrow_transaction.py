from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class BorrowTransaction:
    Id: int
    BookId: int
    UserId: int
    BorrowDate: datetime
    ReturnDate: datetime
    RealReturnDate: Optional[datetime] = None
    BookTitle: Optional[str] = None
    UserName: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.Id,
            "bookId": self.BookId,
            "userId": self.UserId,
            "borrowDate": self.BorrowDate.strftime("%Y-%m-%d %H:%M:%S") if self.BorrowDate else None,
            "returnDate": self.ReturnDate.strftime("%Y-%m-%d %H:%M:%S") if self.ReturnDate else None,
            "realReturnDate": self.RealReturnDate.strftime("%Y-%m-%d %H:%M:%S") if self.RealReturnDate else None,
            "state": "İade Edildi" if self.RealReturnDate else "Ödünçte",
            "bookTitle": self.BookTitle or "",
            "userName": self.UserName or ""
        }
    
    def is_returned(self) -> bool:
        return self.RealReturnDate is not None

"""STATS_SERVICE.PY - İstatistik Servisi"""
from config import DatabaseConfig
from repositories.penalty_repository import PenaltyRepository
from repositories.transaction_repository import TransactionRepository

class StatsService:
    def __init__(self):
        self.penalty_repo = PenaltyRepository()
        self.tx_repo = TransactionRepository()
    
    def get_admin_stats(self) -> dict:
        conn = None
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM Books")
            total_books = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM Users")
            total_users = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM BorrowTransactions WHERE RealReturnDate IS NULL")
            active_borrows = cursor.fetchone()[0] or 0
            
            total_penalties = self.penalty_repo.get_total_amount()
            
            return {
                "totalBooks": total_books,
                "totalUsers": total_users,
                "activeBorrows": active_borrows,
                "totalPenalties": total_penalties
            }
        except Exception as e:
            print(f"[StatsService.get_admin_stats] HATA: {e}")
            return {"totalBooks": 0, "totalUsers": 0, "activeBorrows": 0, "totalPenalties": 0}
        finally:
            if conn: conn.close()
    
    def get_user_stats(self, user_id: int) -> dict:
        try:
            active_borrows = self.tx_repo.count_active_by_user(user_id)
            transactions = self.tx_repo.get_by_user_id(user_id)
            total_penalties = self.penalty_repo.get_user_total_amount(user_id)
            
            return {
                "activeBorrows": active_borrows,
                "totalTransactions": len(transactions),
                "totalPenalties": total_penalties
            }
        except Exception as e:
            print(f"[StatsService.get_user_stats] HATA: {e}")
            return {"activeBorrows": 0, "totalTransactions": 0, "totalPenalties": 0}

stats_service = StatsService()

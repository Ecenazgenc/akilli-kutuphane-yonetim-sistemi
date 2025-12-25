"""
BOOK_REPOSITORY.PY - Kitap Veritabanı İşlemleri
"""
from typing import List, Optional
from repositories.base_repository import BaseRepository
from entities.book import Book

class BookRepository(BaseRepository):
    
    def get_all(self) -> List[Book]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.Id, b.Title, b.AuthorId, b.CategoryId, b.StockNumber, b.YearOfpublication,
                       ISNULL(a.Name + ' ' + a.LastName, '') AS AuthorName,
                       ISNULL(c.Name, '') AS CategoryName,
                       b.StockNumber - ISNULL((
                           SELECT COUNT(*) FROM BorrowTransactions bt 
                           WHERE bt.BookId = b.Id AND bt.RealReturnDate IS NULL
                       ), 0) AS Available
                FROM Books b
                LEFT JOIN Authors a ON b.AuthorId = a.Id
                LEFT JOIN Categories c ON b.CategoryId = c.Id
            """)
            books = []
            for row in cursor.fetchall():
                books.append(Book(
                    Id=row[0], Title=row[1], AuthorId=row[2], CategoryId=row[3],
                    StockNumber=row[4], YearOfpublication=row[5],
                    AuthorName=row[6], CategoryName=row[7], Available=row[8]
                ))
            return books
        except Exception as e:
            print(f"[BookRepository.get_all] HATA: {e}")
            return []
        finally:
            if conn: conn.close()
    
    def get_by_id(self, book_id: int) -> Optional[Book]:
        if not self.validate_id(book_id):
            return None
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.Id, b.Title, b.AuthorId, b.CategoryId, b.StockNumber, b.YearOfpublication,
                       ISNULL(a.Name + ' ' + a.LastName, '') AS AuthorName,
                       ISNULL(c.Name, '') AS CategoryName,
                       b.StockNumber - ISNULL((
                           SELECT COUNT(*) FROM BorrowTransactions bt 
                           WHERE bt.BookId = b.Id AND bt.RealReturnDate IS NULL
                       ), 0) AS Available
                FROM Books b
                LEFT JOIN Authors a ON b.AuthorId = a.Id
                LEFT JOIN Categories c ON b.CategoryId = c.Id
                WHERE b.Id = ?
            """, (book_id,))
            row = cursor.fetchone()
            if row:
                return Book(
                    Id=row[0], Title=row[1], AuthorId=row[2], CategoryId=row[3],
                    StockNumber=row[4], YearOfpublication=row[5],
                    AuthorName=row[6], CategoryName=row[7], Available=row[8]
                )
            return None
        except Exception as e:
            print(f"[BookRepository.get_by_id] HATA: {e}")
            return None
        finally:
            if conn: conn.close()
    
    def add(self, title: str, author_id: int, category_id: int, stock: int, year: int) -> Optional[Book]:
        if not self.validate_input(title) or not self.validate_id(author_id) or not self.validate_id(category_id):
            return None
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Books (Title, AuthorId, CategoryId, StockNumber, YearOfpublication) VALUES (?, ?, ?, ?, ?); SELECT SCOPE_IDENTITY();",
                (title, author_id, category_id, stock, year)
            )
            cursor.nextset()
            new_id = cursor.fetchone()[0]
            conn.commit()
            return self.get_by_id(int(new_id))
        except Exception as e:
            print(f"[BookRepository.add] HATA: {e}")
            return None
        finally:
            if conn: conn.close()
    
    def update(self, book_id: int, title: str, author_id: int, category_id: int, stock: int, year: int) -> bool:
        if not self.validate_id(book_id) or not self.validate_input(title):
            return False
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Books SET Title = ?, AuthorId = ?, CategoryId = ?, StockNumber = ?, YearOfpublication = ? WHERE Id = ?",
                (title, author_id, category_id, stock, year, book_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[BookRepository.update] HATA: {e}")
            return False
        finally:
            if conn: conn.close()
    
    def delete(self, book_id: int) -> bool:
        if not self.validate_id(book_id):
            return False
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Books WHERE Id = ?", (book_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[BookRepository.delete] HATA: {e}")
            return False
        finally:
            if conn: conn.close()

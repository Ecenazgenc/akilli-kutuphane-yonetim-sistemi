/*
=============================================================================
KUTUPHANE_DB.SQL - VERİTABANI + TRIGGER + STORED PROCEDURE
=============================================================================

CEZA SİSTEMİ:
- İade süresi: 1 dakika
- Gecikme cezası: 5 TL / dakika

SQL BİLEŞENLERİ:
- trg_CalculatePenalty: Otomatik ceza hesaplama (TRIGGER)
- sp_BorrowBook: Kitap ödünç alma (PROCEDURE)
- sp_ReturnBook: Kitap iade etme (PROCEDURE)
- sp_PayPenalty: Ceza ödeme (PROCEDURE)
=============================================================================
*/

-- Veritabanı oluşturma
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'KutuphaneDB')
BEGIN
    ALTER DATABASE KutuphaneDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE KutuphaneDB;
END
GO

CREATE DATABASE KutuphaneDB;
GO

USE KutuphaneDB;
GO

-- =============================================
-- TABLOLAR
-- =============================================

CREATE TABLE Users (
    Id INT PRIMARY KEY IDENTITY(1,1),
    FullName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(256) NOT NULL,
    Role NVARCHAR(20) NOT NULL DEFAULT 'user'
);
GO

CREATE TABLE Authors (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Country NVARCHAR(50)
);
GO

CREATE TABLE Categories (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(50) NOT NULL
);
GO

CREATE TABLE Books (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Title NVARCHAR(200) NOT NULL,
    AuthorId INT NOT NULL,
    CategoryId INT NOT NULL,
    StockNumber INT NOT NULL DEFAULT 1,
    YearOfpublication INT,
    CONSTRAINT FK_Books_Authors FOREIGN KEY (AuthorId) REFERENCES Authors(Id) ON DELETE CASCADE,
    CONSTRAINT FK_Books_Categories FOREIGN KEY (CategoryId) REFERENCES Categories(Id) ON DELETE CASCADE
);
GO

CREATE TABLE BorrowTransactions (
    Id INT PRIMARY KEY IDENTITY(1,1),
    BookId INT NOT NULL,
    UserId INT NOT NULL,
    BorrowDate DATETIME NOT NULL,
    ReturnDate DATETIME NOT NULL,
    RealReturnDate DATETIME NULL,
    CONSTRAINT FK_BorrowTransactions_Books FOREIGN KEY (BookId) REFERENCES Books(Id) ON DELETE CASCADE,
    CONSTRAINT FK_BorrowTransactions_Users FOREIGN KEY (UserId) REFERENCES Users(Id) ON DELETE CASCADE
);
GO

CREATE TABLE Penalties (
    Id INT PRIMARY KEY IDENTITY(1,1),
    BorrowTransactionsId INT NOT NULL,
    NumberOfDay INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    CreatedDate DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Penalties_BorrowTransactions FOREIGN KEY (BorrowTransactionsId) REFERENCES BorrowTransactions(Id) ON DELETE CASCADE
);
GO

-- =============================================
-- TRIGGER: trg_CalculatePenalty
-- İade yapıldığında otomatik ceza hesaplar
-- =============================================
CREATE TRIGGER trg_CalculatePenalty
ON BorrowTransactions
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @TransactionId INT;
    DECLARE @ReturnDate DATETIME;
    DECLARE @RealReturnDate DATETIME;
    DECLARE @OldRealReturnDate DATETIME;
    DECLARE @DelayMinutes INT;
    DECLARE @PenaltyAmount DECIMAL(10,2);
    DECLARE @PenaltyPerMinute DECIMAL(10,2) = 5.00; -- 5 TL/dakika
    
    SELECT 
        @TransactionId = i.Id,
        @ReturnDate = i.ReturnDate,
        @RealReturnDate = i.RealReturnDate,
        @OldRealReturnDate = d.RealReturnDate
    FROM inserted i
    INNER JOIN deleted d ON i.Id = d.Id;
    
    -- RealReturnDate NULL'dan değere geçtiyse (iade yapılıyor)
    IF @OldRealReturnDate IS NULL AND @RealReturnDate IS NOT NULL
    BEGIN
        -- Gecikme var mı?
        IF @RealReturnDate > @ReturnDate
        BEGIN
            SET @DelayMinutes = DATEDIFF(MINUTE, @ReturnDate, @RealReturnDate);
            IF @DelayMinutes < 1 SET @DelayMinutes = 1;
            
            SET @PenaltyAmount = @DelayMinutes * @PenaltyPerMinute;
            
            INSERT INTO Penalties (BorrowTransactionsId, NumberOfDay, Amount, CreatedDate)
            VALUES (@TransactionId, @DelayMinutes, @PenaltyAmount, GETDATE());
        END
    END
END;
GO

-- =============================================
-- STORED PROCEDURE: sp_BorrowBook
-- Kitap ödünç alma
-- =============================================
CREATE PROCEDURE sp_BorrowBook
    @BookId INT,
    @UserId INT,
    @LoanDurationMinutes INT = 1,
    @NewTransactionId INT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    
    DECLARE @AvailableStock INT;
    DECLARE @BorrowDate DATETIME;
    DECLARE @ReturnDate DATETIME;
    DECLARE @HasActiveBorrow INT;
    DECLARE @HasUnpaidPenalty INT;
    
    SET @NewTransactionId = 0;
    SET @ErrorMessage = '';
    SET @BorrowDate = GETDATE();
    SET @ReturnDate = DATEADD(MINUTE, @LoanDurationMinutes, @BorrowDate);
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Kitap var mı?
        IF NOT EXISTS (SELECT 1 FROM Books WHERE Id = @BookId)
        BEGIN
            SET @ErrorMessage = 'Kitap bulunamadı';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Stokta var mı?
        SELECT @AvailableStock = b.StockNumber - ISNULL((
            SELECT COUNT(*) FROM BorrowTransactions bt 
            WHERE bt.BookId = b.Id AND bt.RealReturnDate IS NULL
        ), 0)
        FROM Books b WHERE b.Id = @BookId;
        
        IF @AvailableStock <= 0
        BEGIN
            SET @ErrorMessage = 'Kitap stokta yok';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Aynı kitabı zaten almış mı?
        SELECT @HasActiveBorrow = COUNT(*) 
        FROM BorrowTransactions 
        WHERE UserId = @UserId AND BookId = @BookId AND RealReturnDate IS NULL;
        
        IF @HasActiveBorrow > 0
        BEGIN
            SET @ErrorMessage = 'Bu kitabı zaten ödünç almışsınız';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Ödenmemiş ceza var mı?
        SELECT @HasUnpaidPenalty = COUNT(*) 
        FROM Penalties p
        INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
        WHERE bt.UserId = @UserId;
        
        IF @HasUnpaidPenalty > 0
        BEGIN
            SET @ErrorMessage = 'Ödenmemiş cezanız var. Önce cezanızı ödeyin.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- İşlemi kaydet
        INSERT INTO BorrowTransactions (BookId, UserId, BorrowDate, ReturnDate)
        VALUES (@BookId, @UserId, @BorrowDate, @ReturnDate);
        
        SET @NewTransactionId = SCOPE_IDENTITY();
        
        COMMIT TRANSACTION;
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        SET @ErrorMessage = ERROR_MESSAGE();
    END CATCH
END;
GO

-- =============================================
-- STORED PROCEDURE: sp_ReturnBook
-- Kitap iade etme
-- =============================================
CREATE PROCEDURE sp_ReturnBook
    @TransactionId INT,
    @UserId INT,
    @Success BIT OUTPUT,
    @Message NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    
    DECLARE @ActualUserId INT;
    DECLARE @RealReturnDate DATETIME;
    DECLARE @ReturnDate DATETIME;
    DECLARE @BookTitle NVARCHAR(200);
    DECLARE @DelayMinutes INT;
    
    SET @Success = 0;
    SET @Message = '';
    
    BEGIN TRY
        SELECT 
            @ActualUserId = bt.UserId,
            @RealReturnDate = bt.RealReturnDate,
            @ReturnDate = bt.ReturnDate,
            @BookTitle = b.Title
        FROM BorrowTransactions bt
        INNER JOIN Books b ON bt.BookId = b.Id
        WHERE bt.Id = @TransactionId;
        
        IF @ActualUserId IS NULL
        BEGIN
            SET @Message = 'İşlem bulunamadı';
            RETURN;
        END
        
        IF @ActualUserId <> @UserId
        BEGIN
            SET @Message = 'Bu işlem size ait değil';
            RETURN;
        END
        
        IF @RealReturnDate IS NOT NULL
        BEGIN
            SET @Message = 'Kitap zaten iade edilmiş';
            RETURN;
        END
        
        -- İade işlemi (Trigger ceza hesaplayacak)
        UPDATE BorrowTransactions 
        SET RealReturnDate = GETDATE()
        WHERE Id = @TransactionId;
        
        -- Mesaj oluştur
        DECLARE @NewRealReturnDate DATETIME;
        SELECT @NewRealReturnDate = RealReturnDate FROM BorrowTransactions WHERE Id = @TransactionId;
        
        IF @NewRealReturnDate > @ReturnDate
        BEGIN
            SET @DelayMinutes = DATEDIFF(MINUTE, @ReturnDate, @NewRealReturnDate);
            IF @DelayMinutes < 1 SET @DelayMinutes = 1;
            
            SET @Message = '''' + @BookTitle + ''' iade edildi. ' + 
                          CAST(@DelayMinutes AS VARCHAR) + ' dakika gecikme için ' + 
                          CAST(@DelayMinutes * 5 AS VARCHAR) + ' TL ceza kesildi!';
        END
        ELSE
        BEGIN
            SET @Message = '''' + @BookTitle + ''' başarıyla iade edildi. Teşekkürler!';
        END
        
        SET @Success = 1;
        
    END TRY
    BEGIN CATCH
        SET @Message = ERROR_MESSAGE();
    END CATCH
END;
GO

-- =============================================
-- STORED PROCEDURE: sp_PayPenalty
-- Ceza ödeme
-- =============================================
CREATE PROCEDURE sp_PayPenalty
    @PenaltyId INT,
    @UserId INT,
    @Success BIT OUTPUT,
    @Message NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    
    DECLARE @Amount DECIMAL(10,2);
    DECLARE @ActualUserId INT;
    
    SET @Success = 0;
    SET @Message = '';
    
    SELECT @Amount = p.Amount, @ActualUserId = bt.UserId
    FROM Penalties p
    INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
    WHERE p.Id = @PenaltyId;
    
    IF @Amount IS NULL
    BEGIN
        SET @Message = 'Ceza bulunamadı';
        RETURN;
    END
    
    IF @ActualUserId <> @UserId
    BEGIN
        SET @Message = 'Bu ceza size ait değil';
        RETURN;
    END
    
    DELETE FROM Penalties WHERE Id = @PenaltyId;
    
    SET @Success = 1;
    SET @Message = CAST(@Amount AS VARCHAR) + ' TL ceza başarıyla ödendi';
END;
GO

-- =============================================
-- ÖRNEK VERİLER
-- =============================================

-- Admin (şifre: 123456)
INSERT INTO Users (FullName, Email, PasswordHash, Role) VALUES
('Admin Kullanıcı', 'admin@kutuphane.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin');

-- Test kullanıcısı (şifre: 123456)
INSERT INTO Users (FullName, Email, PasswordHash, Role) VALUES
('Test Kullanıcı', 'test@test.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user');

-- Yazarlar
INSERT INTO Authors (Name, LastName, Country) VALUES
('Fyodor', 'Dostoyevski', 'Rusya'),
('Lev', 'Tolstoy', 'Rusya'),
('Orhan', 'Pamuk', 'Türkiye'),
('Sabahattin', 'Ali', 'Türkiye'),
('Gabriel Garcia', 'Marquez', 'Kolombiya');

-- Kategoriler
INSERT INTO Categories (Name) VALUES
('Roman'), ('Bilim Kurgu'), ('Tarih'), ('Felsefe'), ('Şiir');

-- Kitaplar
INSERT INTO Books (Title, AuthorId, CategoryId, StockNumber, YearOfpublication) VALUES
('Suç ve Ceza', 1, 1, 3, 1866),
('Savaş ve Barış', 2, 1, 2, 1869),
('Masumiyet Müzesi', 3, 1, 4, 2008),
('Kürk Mantolu Madonna', 4, 1, 5, 1943),
('Yüzyıllık Yalnızlık', 5, 1, 3, 1967),
('Karamazov Kardeşler', 1, 1, 2, 1880),
('Anna Karenina', 2, 1, 3, 1877);
GO

PRINT '========================================';
PRINT 'VERİTABANI OLUŞTURULDU';
PRINT '========================================';
PRINT 'Trigger: trg_CalculatePenalty';
PRINT 'Procedure: sp_BorrowBook';
PRINT 'Procedure: sp_ReturnBook';
PRINT 'Procedure: sp_PayPenalty';
PRINT '========================================';
PRINT 'Ceza: 5 TL/dakika, İade süresi: 1 dakika';
PRINT '========================================';
PRINT 'Admin: admin@kutuphane.com / 123456';
PRINT 'Üye: test@test.com / 123456';
PRINT '========================================';
GO

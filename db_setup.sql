/*
================================================================================
TRIGGER VE STORED PROCEDURE DOSYASI
================================================================================
Kütüphane Yönetim Sistemi - Veritabanı Otomasyonu
Bu dosya şunları içerir:
1. trg_CalculatePenalty   - Otomatik ceza hesaplama TRIGGER'ı
2. sp_BorrowBook          - Kitap ödünç alma STORED PROCEDURE
3. sp_ReturnBook          - Kitap iade STORED PROCEDURE  
4. sp_PayPenalty          - Ceza ödeme STORED PROCEDURE
================================================================================
*/
USE KutuphaneDB;
GO

-- Eğer trigger varsa önce sil
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'trg_CalculatePenalty')
BEGIN
    DROP TRIGGER trg_CalculatePenalty;
    PRINT 'Eski trg_CalculatePenalty trigger silindi.';
END
GO

-- Trigger'ı oluştur
CREATE TRIGGER trg_CalculatePenalty
ON BorrowTransactions          -- Bu tablo üzerinde çalışacak
AFTER UPDATE                   -- UPDATE işleminden SONRA tetiklenecek
AS
BEGIN
   SET NOCOUNT ON;
    
    -- Değişkenleri tanımla
    DECLARE @TransactionId INT;         -- İşlem ID'si
    DECLARE @ReturnDate DATETIME;        -- Planlanan son iade tarihi
    DECLARE @RealReturnDate DATETIME;    -- Gerçek iade tarihi (yeni değer)
    DECLARE @OldRealReturnDate DATETIME; -- Gerçek iade tarihi (eski değer)
    DECLARE @DelayMinutes INT;           -- Gecikme süresi (dakika)
    DECLARE @PenaltyAmount DECIMAL(10,2); -- Ceza tutarı (TL)
  
    SELECT 
        @TransactionId = i.Id,
        @ReturnDate = i.ReturnDate,
        @RealReturnDate = i.RealReturnDate
    FROM INSERTED i;
    
    /*
    DELETED tablosundan eski değeri al
    - UPDATE öncesi değerler burada
    - Karşılaştırma için kullanıyoruz
    */
    SELECT @OldRealReturnDate = d.RealReturnDate
    FROM DELETED d;
    
    -- Debug çıktıları (SSMS'de Messages sekmesinde görünür)
    PRINT '========================================';
    PRINT 'TRIGGER ÇALIŞTI: trg_CalculatePenalty';
    PRINT '========================================';
    PRINT 'İşlem ID: ' + CAST(@TransactionId AS VARCHAR);
    PRINT 'Eski RealReturnDate: ' + ISNULL(CAST(@OldRealReturnDate AS VARCHAR), 'NULL');
    PRINT 'Yeni RealReturnDate: ' + ISNULL(CAST(@RealReturnDate AS VARCHAR), 'NULL');
    PRINT 'Planlanan ReturnDate: ' + CAST(@ReturnDate AS VARCHAR);
   
    IF @OldRealReturnDate IS NULL 
       AND @RealReturnDate IS NOT NULL 
       AND @RealReturnDate > @ReturnDate
    BEGIN
        PRINT '----------------------------------------';
        PRINT 'GECİKME TESPİT EDİLDİ!';
        
      
        SET @DelayMinutes = DATEDIFF(MINUTE, @ReturnDate, @RealReturnDate);
        
        SET @PenaltyAmount = @DelayMinutes * 5.0;
        
        PRINT 'Gecikme Süresi: ' + CAST(@DelayMinutes AS VARCHAR) + ' dakika';
        PRINT 'Ceza Tutarı: ' + CAST(@PenaltyAmount AS VARCHAR) + ' TL';
        
        INSERT INTO Penalties (
            BorrowTransactionsId, 
            NumberOfDay, 
            Amount, 
            CreatedDate
        )
        VALUES (
            @TransactionId, 
            @DelayMinutes, 
            @PenaltyAmount, 
            GETDATE()
        );
        
        PRINT 'CEZA KAYDI OLUŞTURULDU!';
        PRINT '----------------------------------------';
    END
    ELSE
    BEGIN
        PRINT 'Gecikme yok veya zaten iade edilmiş.';
    END
    
    PRINT '========================================';
END
GO

PRINT 'trg_CalculatePenalty trigger başarıyla oluşturuldu.';
PRINT '';
GO


/*
================================================================================
2. STORED PROCEDURE: sp_BorrowBook
================================================================================
Açıklama:
    Kitap ödünç alma işlemini gerçekleştirir.
    Tüm kontrolleri yapar ve uygunsa ödünç kaydı oluşturur.
================================================================================
*/

-- Eğer procedure varsa önce sil
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_BorrowBook')
BEGIN
    DROP PROCEDURE sp_BorrowBook;
    PRINT 'Eski sp_BorrowBook procedure silindi.';
END
GO

-- Procedure'ı oluştur
CREATE PROCEDURE sp_BorrowBook
    @BookId INT,                      -- Ödünç alınacak kitap
    @UserId INT,                      -- Ödünç alan kullanıcı
    @LoanDurationMinutes INT = 1      -- Ödünç süresi (varsayılan 1 dakika - test için)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Değişkenler
    DECLARE @StockNumber INT;         -- Toplam stok sayısı
    DECLARE @BorrowedCount INT;       -- Ödünçte olan sayısı
    DECLARE @Available INT;           -- Müsait stok
    DECLARE @AlreadyBorrowed INT;     -- Kullanıcı aynı kitabı almış mı
    DECLARE @HasPenalty INT;          -- Ödenmemiş ceza var mı
    DECLARE @ReturnDate DATETIME;     -- Son iade tarihi
    DECLARE @NewTransactionId INT;    -- Yeni işlem ID'si
    
    PRINT '========================================';
    PRINT 'sp_BorrowBook ÇALIŞIYOR';
    PRINT 'BookId: ' + CAST(@BookId AS VARCHAR);
    PRINT 'UserId: ' + CAST(@UserId AS VARCHAR);
    PRINT '========================================';
    
    /*
    KONTROL 1: Kitap var mı?
    - Books tablosunda ID ile arama yapılır
    - Bulunamazsa @StockNumber NULL kalır
    */
    SELECT @StockNumber = StockNumber 
    FROM Books 
    WHERE Id = @BookId;
    
    IF @StockNumber IS NULL
    BEGIN
        PRINT 'HATA: Kitap bulunamadı!';
        -- Sonuç döndür: Başarısız
        SELECT 0 AS Success, 
               'Kitap bulunamadı' AS Message, 
               NULL AS TransactionId;
        RETURN; -- Procedure'dan çık
    END
    
    PRINT 'Kitap bulundu. Toplam stok: ' + CAST(@StockNumber AS VARCHAR);
    
    /*
    KONTROL 2: Stokta kitap var mı?
    - Ödünçte olan kitapları say (RealReturnDate IS NULL = iade edilmemiş)
    - Müsait = Toplam - Ödünçte olan
    */
    SELECT @BorrowedCount = COUNT(*) 
    FROM BorrowTransactions 
    WHERE BookId = @BookId 
      AND RealReturnDate IS NULL;  -- İade edilmemiş olanlar
    
    SET @Available = @StockNumber - @BorrowedCount;
    
    PRINT 'Ödünçte olan: ' + CAST(@BorrowedCount AS VARCHAR);
    PRINT 'Müsait stok: ' + CAST(@Available AS VARCHAR);
    
    IF @Available <= 0
    BEGIN
        PRINT 'HATA: Kitap stokta yok!';
        SELECT 0 AS Success, 
               'Kitap stokta yok' AS Message, 
               NULL AS TransactionId;
        RETURN;
    END
    
    /*
    KONTROL 3: Kullanıcı aynı kitabı zaten almış mı?
    - Aynı kullanıcı aynı kitabı birden fazla kez alamaz
    - İade etmeden yeni ödünç yapamaz
    */
    SELECT @AlreadyBorrowed = COUNT(*) 
    FROM BorrowTransactions 
    WHERE BookId = @BookId 
      AND UserId = @UserId 
      AND RealReturnDate IS NULL;  -- Henüz iade etmemiş
    
    IF @AlreadyBorrowed > 0
    BEGIN
        PRINT 'HATA: Kullanıcı bu kitabı zaten almış!';
        SELECT 0 AS Success, 
               'Bu kitabı zaten ödünç aldınız' AS Message, 
               NULL AS TransactionId;
        RETURN;
    END
    
    /*
    KONTROL 4: Ödenmemiş ceza var mı?
    - Cezası olan kullanıcı yeni kitap alamaz
    - Önce cezasını ödemeli
    */
    SELECT @HasPenalty = COUNT(*) 
    FROM Penalties p
    INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
    WHERE bt.UserId = @UserId;
    
    IF @HasPenalty > 0
    BEGIN
        PRINT 'HATA: Kullanıcının ödenmemiş cezası var!';
        SELECT 0 AS Success, 
               'Ödenmemiş cezanız var. Önce cezayı ödeyin.' AS Message, 
               NULL AS TransactionId;
        RETURN;
    END
    
    /*
    TÜM KONTROLLER GEÇTİ - ÖDÜNÇ KAYDI OLUŞTUR
    
    DATEADD fonksiyonu:
    - Tarihe belirtilen miktarda zaman ekler
    - DATEADD(birim, miktar, tarih)
    - Örnek: DATEADD(MINUTE, 1, GETDATE()) = Şu andan 1 dakika sonra
    
    GETDATE():
    - Şu anki tarih ve saati döndürür
    - SQL Server'ın sistem saatini kullanır
    */
    SET @ReturnDate = DATEADD(MINUTE, @LoanDurationMinutes, GETDATE());
    
    PRINT 'Ödünç tarihi: ' + CONVERT(VARCHAR, GETDATE(), 120);
    PRINT 'Son iade tarihi: ' + CONVERT(VARCHAR, @ReturnDate, 120);
    
    -- BorrowTransactions tablosuna kayıt ekle
    INSERT INTO BorrowTransactions (
        BookId, 
        UserId, 
        BorrowDate, 
        ReturnDate, 
        RealReturnDate
    )
    VALUES (
        @BookId, 
        @UserId, 
        GETDATE(),        -- Şu an
        @ReturnDate,      -- Son iade tarihi
        NULL              -- Henüz iade edilmedi
    );
    
    /*
    SCOPE_IDENTITY():
    - Son INSERT işleminde oluşturulan IDENTITY değerini döndürür
    - Sadece mevcut scope'taki (bu procedure) değeri döndürür
    - @@IDENTITY'den daha güvenli (trigger'lardan etkilenmez)
    */
    SET @NewTransactionId = SCOPE_IDENTITY();
    
    PRINT 'BAŞARILI! Yeni işlem ID: ' + CAST(@NewTransactionId AS VARCHAR);
    PRINT '========================================';
    
    -- Başarılı sonuç döndür
    SELECT 1 AS Success, 
           'Kitap ödünç alındı. Son iade: ' + CONVERT(VARCHAR, @ReturnDate, 120) AS Message, 
           @NewTransactionId AS TransactionId;
END
GO

PRINT 'sp_BorrowBook procedure başarıyla oluşturuldu.';
PRINT '';
GO


/*
================================================================================
3. STORED PROCEDURE: sp_ReturnBook
================================================================================
Açıklama:
    Kitap iade işlemini gerçekleştirir.
    RealReturnDate'i günceller ve trigger'ı tetikler.

Parametreler:
    @TransactionId INT - İade edilecek işlemin ID'si
    @UserId INT        - İade eden kullanıcının ID'si

Kontroller:
    1. İşlem var mı?
    2. İşlem bu kullanıcıya mı ait?
    3. Kitap zaten iade edilmiş mi?

Önemli:
    - Bu procedure RealReturnDate'i günceller
    - UPDATE işlemi trg_CalculatePenalty trigger'ını tetikler
    - Trigger otomatik olarak gecikme cezasını hesaplar
    - Procedure, trigger çalıştıktan sonra ceza tutarını kontrol eder
================================================================================
*/

-- Eğer procedure varsa önce sil
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_ReturnBook')
BEGIN
    DROP PROCEDURE sp_ReturnBook;
    PRINT 'Eski sp_ReturnBook procedure silindi.';
END
GO

-- Procedure'ı oluştur
CREATE PROCEDURE sp_ReturnBook
    @TransactionId INT,   -- İade edilecek işlem
    @UserId INT           -- İade eden kullanıcı
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @OwnerUserId INT;         -- İşlemin sahibi
    DECLARE @RealReturnDate DATETIME; -- Mevcut iade tarihi
    DECLARE @PenaltyAmount DECIMAL(10,2); -- Oluşan ceza
    
    PRINT '========================================';
    PRINT 'sp_ReturnBook ÇALIŞIYOR';
    PRINT 'TransactionId: ' + CAST(@TransactionId AS VARCHAR);
    PRINT 'UserId: ' + CAST(@UserId AS VARCHAR);
    PRINT '========================================';
    
    /*
    KONTROL 1: İşlem var mı ve kime ait?
    */
    SELECT @OwnerUserId = UserId, 
           @RealReturnDate = RealReturnDate
    FROM BorrowTransactions 
    WHERE Id = @TransactionId;
    
    IF @OwnerUserId IS NULL
    BEGIN
        PRINT 'HATA: İşlem bulunamadı!';
        SELECT 0 AS Success, 
               'İşlem bulunamadı' AS Message, 
               NULL AS PenaltyAmount;
        RETURN;
    END
    
    /*
    KONTROL 2: Kullanıcı kontrolü
    - Sadece kendi ödünç aldığı kitabı iade edebilir
    */
    IF @OwnerUserId != @UserId
    BEGIN
        PRINT 'HATA: Bu işlem kullanıcıya ait değil!';
        SELECT 0 AS Success, 
               'Bu işlem size ait değil' AS Message, 
               NULL AS PenaltyAmount;
        RETURN;
    END
    
    /*
    KONTROL 3: Zaten iade edilmiş mi?
    - RealReturnDate NULL değilse zaten iade edilmiş
    */
    IF @RealReturnDate IS NOT NULL
    BEGIN
        PRINT 'HATA: Kitap zaten iade edilmiş!';
        SELECT 0 AS Success, 
               'Bu kitap zaten iade edilmiş' AS Message, 
               NULL AS PenaltyAmount;
        RETURN;
    END
    
    /*
    İADE İŞLEMİ
    - RealReturnDate'i şu anki tarih/saat ile güncelle
    - Bu UPDATE işlemi trg_CalculatePenalty TRIGGER'ını tetikler!
    - Trigger, gecikme varsa otomatik olarak Penalties tablosuna kayıt ekler
    */
    PRINT 'İade işlemi yapılıyor...';
    PRINT 'Gerçek iade tarihi: ' + CONVERT(VARCHAR, GETDATE(), 120);
    
    UPDATE BorrowTransactions 
    SET RealReturnDate = GETDATE()
    WHERE Id = @TransactionId;
    
    PRINT 'UPDATE tamamlandı. Trigger çalışmış olmalı.';
    
    /*
    CEZA KONTROLÜ
    - Trigger çalıştıktan sonra Penalties tablosunu kontrol et
    - Eğer bu işlem için ceza kaydı varsa, tutarını al
    */
    SELECT @PenaltyAmount = Amount 
    FROM Penalties 
    WHERE BorrowTransactionsId = @TransactionId;
    
    -- Sonucu döndür
    IF @PenaltyAmount IS NOT NULL AND @PenaltyAmount > 0
    BEGIN
        PRINT 'UYARI: Gecikme cezası oluştu!';
        PRINT 'Ceza tutarı: ' + CAST(@PenaltyAmount AS VARCHAR) + ' TL';
        
        SELECT 1 AS Success, 
               'Kitap iade edildi. Gecikme cezası: ' + CAST(@PenaltyAmount AS VARCHAR) + ' TL' AS Message, 
               @PenaltyAmount AS PenaltyAmount;
    END
    ELSE
    BEGIN
        PRINT 'Zamanında iade edildi, ceza yok.';
        
        SELECT 1 AS Success, 
               'Kitap başarıyla iade edildi' AS Message, 
               0 AS PenaltyAmount;
    END
    
    PRINT '========================================';
END
GO

PRINT 'sp_ReturnBook procedure başarıyla oluşturuldu.';
PRINT '';
GO


/*
================================================================================
4. STORED PROCEDURE: sp_PayPenalty
================================================================================
Açıklama:
    Ceza ödeme işlemini gerçekleştirir.
    Ödeme = Ceza kaydının silinmesi

Parametreler:
    @PenaltyId INT - Ödenecek cezanın ID'si
    @UserId INT    - Ödeyen kullanıcının ID'si

Kontroller:
    1. Ceza var mı?
    2. Ceza bu kullanıcıya mı ait?

Başarılıysa:
    - Penalties tablosundan ceza kaydı silinir
    - Kullanıcı artık yeni kitap ödünç alabilir
================================================================================
*/

-- Eğer procedure varsa önce sil
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_PayPenalty')
BEGIN
    DROP PROCEDURE sp_PayPenalty;
    PRINT 'Eski sp_PayPenalty procedure silindi.';
END
GO

-- Procedure'ı oluştur
CREATE PROCEDURE sp_PayPenalty
    @PenaltyId INT,   -- Ödenecek ceza
    @UserId INT       -- Ödeyen kullanıcı
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @PenaltyUserId INT;       -- Cezanın sahibi
    DECLARE @Amount DECIMAL(10,2);    -- Ceza tutarı
    
    PRINT '========================================';
    PRINT 'sp_PayPenalty ÇALIŞIYOR';
    PRINT 'PenaltyId: ' + CAST(@PenaltyId AS VARCHAR);
    PRINT 'UserId: ' + CAST(@UserId AS VARCHAR);
    PRINT '========================================';
    
    /*
    KONTROL 1: Ceza var mı ve kime ait?
    - Penalties tablosu BorrowTransactions ile JOIN edilir
    - UserId, BorrowTransactions tablosunda
    */
    SELECT @PenaltyUserId = bt.UserId, 
           @Amount = p.Amount
    FROM Penalties p
    INNER JOIN BorrowTransactions bt ON p.BorrowTransactionsId = bt.Id
    WHERE p.Id = @PenaltyId;
    
    IF @PenaltyUserId IS NULL
    BEGIN
        PRINT 'HATA: Ceza bulunamadı!';
        SELECT 0 AS Success, 
               'Ceza bulunamadı' AS Message;
        RETURN;
    END
    
    PRINT 'Ceza bulundu. Tutar: ' + CAST(@Amount AS VARCHAR) + ' TL';
    
    /*
    KONTROL 2: Kullanıcı kontrolü
    - Sadece kendi cezasını ödeyebilir
    */
    IF @PenaltyUserId != @UserId
    BEGIN
        PRINT 'HATA: Bu ceza kullanıcıya ait değil!';
        SELECT 0 AS Success, 
               'Bu ceza size ait değil' AS Message;
        RETURN;
    END
    
    /*
    CEZA ÖDEME = CEZA KAYDINI SİLME
    - Gerçek dünyada burada ödeme işlemi yapılır
    - Bu projede basitlik için silme = ödeme
    */
    PRINT 'Ceza ödeniyor (siliniyor)...';
    
    DELETE FROM Penalties 
    WHERE Id = @PenaltyId;
    
    PRINT 'BAŞARILI! Ceza ödendi.';
    PRINT '========================================';
    
    -- Başarılı sonuç döndür
    SELECT 1 AS Success, 
           CAST(@Amount AS VARCHAR) + ' TL ceza ödendi' AS Message;
END
GO

PRINT 'sp_PayPenalty procedure başarıyla oluşturuldu.';
GO


/*
================================================================================
ÖZET
================================================================================

TRIGGER:
---------
trg_CalculatePenalty
    - BorrowTransactions UPDATE sonrası çalışır
    - Gecikme varsa otomatik ceza hesaplar
    - Penalties tablosuna kayıt ekler
    - Formül: Ceza = Gecikme (dakika) × 5 TL

STORED PROCEDURES:
------------------
sp_BorrowBook(@BookId, @UserId, @LoanDurationMinutes)
    - Kitap ödünç alma
    - Stok, mükerrer ödünç, ceza kontrolleri
    - BorrowTransactions'a kayıt ekler

sp_ReturnBook(@TransactionId, @UserId)
    - Kitap iade
    - RealReturnDate günceller
    - Trigger'ı tetikler

sp_PayPenalty(@PenaltyId, @UserId)
    - Ceza ödeme
    - Penalties'den kayıt siler



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

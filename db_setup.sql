CREATE DATABASE KutuphaneDB;
GO
USE KutuphaneDB;
GO

CREATE TABLE Authors (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    LastName NVARCHAR(100) NOT NULL,
    Country NVARCHAR(100) NOT NULL
);

CREATE TABLE Categories (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL
);

CREATE TABLE Books (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Title NVARCHAR(200) NOT NULL,
    AuthorId INT NOT NULL,
    CategoryId INT NOT NULL,
    StockNumber INT NOT NULL,
    YearOfpublication INT NOT NULL,

    FOREIGN KEY (AuthorId) REFERENCES Authors(Id),
    FOREIGN KEY (CategoryId) REFERENCES Categories(Id)
);
CREATE TABLE Users (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    FullName NVARCHAR(200) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(500) NOT NULL,
    Role NVARCHAR(20) NOT NULL -- admin / user
);
CREATE TABLE BorrowTransactions (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    BookId INT NOT NULL,
    UserId INT NOT NULL,
    BorrowDate DATETIME NOT NULL DEFAULT GETDATE(),
    ReturnDate DATETIME NOT NULL,
    RealReturnDate DATETIME,

    FOREIGN KEY (BookId) REFERENCES Books(Id),
    FOREIGN KEY (UserId) REFERENCES Users(Id)
);
    CREATE TABLE Penalties (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Amount DECIMAL(10,2) NOT NULL,
    BorrowTransactionsId INT ,
    NumberOfDay INT NOT NULL ,
    Date DATE NOT NULL DEFAULT GETDATE(),

    FOREIGN KEY (BorrowTransactionsId) REFERENCES BorrowTransactions(Id)
);
--Tablolara yapılan eklemeler;
INSERT INTO Users (FullName, Email, PasswordHash, Role)
VALUES 
('Enes Kuru', 'enes@example.com', 'kuruenes123', 'user'),
('Zehra Dolak', 'zehra@example.com', '49zehra8', 'user'),
('Ada Korkak', 'ada@example.com', 'adakor123', 'user');

INSERT INTO Authors(Name, LastName,Country)
VALUES 
('Helen', 'Kennerley','İngiltere'),
('Stefan', 'Zweig','Avusturya');

INSERT INTO Categories(Name)
VALUES 
('Roman'),
('Hikaye');


INSERT INTO Books(Title,AuthorId,CategoryId,StockNumber,YearOfpublication)
VALUES 
('Kaygı',2, 1, 67, 2022),
('Bir Çöküşün Öyküsü',1 ,2, 39, 1998);

INSERT INTO BorrowTransactions(BookId,UserId,BorrowDate,ReturnDate,State)
VALUES 
(8, 1, '2025-11-05', '2025-11-15','alındı'),
(9, 2, '2025-11-18', '2025-11-28','alındı');

USE KutuphaneDB;
Go
/*eger bu adda bir prosedur varsa siler*/
IF OBJECT_ID('sp_Borrow', 'P') IS NOT NULL 
    DROP PROCEDURE sp_Borrow;
GO
CREATE PROCEDURE sp_Borrow
    @islem NVARCHAR(10), -- 'Al' veya 'Iade'
    @kullaniciID INT = NULL,
    @oduncID INT = NULL,
    @odunc_tarihi DATE = NULL,
    @iade_tarihi DATE = NULL,
    @gercek_iade_tarihi DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    /*odunc alma*/
    IF @islem = 'Al'
    BEGIN
         IF EXISTS (SELECT 1 FROM Books WHERE Id = @bookId AND StockNumber > 0)
        BEGIN
            INSERT INTO BorrowTransactions(BookId, UserId, BorrowDate, ReturnDate, State)
            VALUES (@bookId, @kullaniciID, ISNULL(@odunc_tarihi, GETDATE()), @iade_tarihi, 'alındı');

            -- stok azaltma
            UPDATE Books SET StockNumber = StockNumber - 1 WHERE Id = @bookId;
        END
        ELSE
        BEGIN
            RAISERROR('Kitap stokta yok.', 16, 1);
        END
    END       
    ELSE IF @islem = 'Iade'
    BEGIN
        UPDATE BorrowTransactions
        SET RealReturnDate = @gercek_iade_tarihi,
            State = 'İade Edildi'
        WHERE Id = @oduncID;
        DECLARE @bId INT;
        SELECT @bId = BookId FROM BorrowTransactions WHERE Id = @oduncID;
        IF @bId IS NOT NULL
            UPDATE Books SET StockNumber = StockNumber + 1 WHERE Id = @bId;
    END
END;
GO

/*gec iade islemleri icin trigger*/
USE KutuphaneDB ;
GO

/* trigger varsa önce siler*/
IF OBJECT_ID('trg_GecIadeCeza', 'TR') IS NOT NULL
    DROP TRIGGER trg_GecIadeCeza;
GO

CREATE TRIGGER trg_GecIadeCeza
ON BorrowTransactions
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    /*Gecikme varsa ve ceza eklenmemişse Ceza tablosuna ekle*/
    INSERT INTO Penalties(BorrowTransactionsId,NumberOfDay, Amount)
    SELECT 
        i.BorrowTransactionsId,
        DATEDIFF(DAY, i.ReturnDate, i.RealReturnDate) AS NumberOfDay,
        DATEDIFF(DAY, i.ReturnDate, i.RealReturnDate) * 5.0 AS Amount,
        CONVERT(date, GETDATE())
    FROM inserted i
    LEFT JOIN Penalties c ON i.BorrowTransactionsId = c.BorrowTransactionsId
    WHERE i.RealReturnDate > i.ReturnDate
      AND c.BorrowTransactionsId IS NULL;
END;
GO
USE KutuphaneDB;
GO

-- Eğer view varsa sil
IF OBJECT_ID('vw_AktifOdunc', 'V') IS NOT NULL
    DROP VIEW vw_AktifOdunc;
GO

CREATE VIEW vw_AktifOdunc
AS
SELECT 
    o.Id,
    b.Title AS kitap_basligi,
    a.Name + ' ' + a.LastName AS Authors,
    u.FullName AS Users,
    o.BorrowDate,
    o.ReturnDate,
    o.state
FROM BorrowTransactions o
INNER JOIN Books b ON o.BookId = b.Id
INNER JOIN Authors a ON b.AuthorId = a.ID
INNER JOIN Users u ON o.UserId = u.Id
WHERE o.RealReturnDate IS NULL;

GO

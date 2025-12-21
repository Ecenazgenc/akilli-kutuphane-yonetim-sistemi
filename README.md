# 📚 Kütüphane Yönetim Sistemi

## Çok Katmanlı Mimari (N-Tier Architecture)

SQL Server bağlantılı, Flask tabanlı kütüphane yönetim sistemi.

---

## 📁 Proje Yapısı

```
kutuphane_proje/
├── app.py                    # Ana uygulama
├── config.py                 # Veritabanı konfigürasyonu
│
├── entities/                 # 📦 ENTITY LAYER (Veri Modelleri)
│   ├── __init__.py
│   ├── user.py
│   ├── author.py
│   ├── category.py
│   ├── book.py
│   ├── borrow_transaction.py
│   └── penalty.py
│
├── repositories/             # 🗄️ REPOSITORY LAYER (Veritabanı İşlemleri)
│   ├── __init__.py
│   ├── base_repository.py
│   ├── user_repository.py
│   ├── author_repository.py
│   ├── category_repository.py
│   ├── book_repository.py
│   ├── transaction_repository.py
│   └── penalty_repository.py
│
├── services/                 # ⚙️ SERVICE LAYER (İş Mantığı)
│   ├── __init__.py
│   ├── auth_service.py
│   ├── user_service.py
│   ├── author_service.py
│   ├── category_service.py
│   ├── book_service.py
│   ├── borrow_service.py
│   ├── penalty_service.py
│   └── stats_service.py
│
├── controllers/              # 🎮 CONTROLLER LAYER (API Endpoints)
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── user_controller.py
│   ├── author_controller.py
│   ├── category_controller.py
│   ├── book_controller.py
│   ├── transaction_controller.py
│   ├── penalty_controller.py
│   ├── member_controller.py
│   └── stats_controller.py
│
├── static/                   # 🌐 VIEW LAYER (Frontend)
│   └── index.html
│
└── sql/                      # 🗃️ SQL Scriptleri
    └── veritabani_kurulum.sql
```

---

## 🏗️ Mimari Açıklama

### 1. Entity Layer (entities/)

### 2. Repository Layer (repositories/)

### 3. Service Layer (services/)

### 4. Controller Layer (controllers/)

### 5. View Layer (static/)

---


## 🔐 Test Hesapları

| Rol | Email | Şifre |
|-----|-------|-------|
| Admin | admin@kutuphane.com | 123456 |
| Üye | test@test.com | 123456 |

---

## ⏱️ Ödünç Sistemi

- **İade Süresi:** 1 dakika (test için)
- **Gecikme Cezası:** 5 TL/dakika
- **Ceza Kontrolü:** Ödenmemiş cezası olan kullanıcı kitap alamaz

---

## 👥 Rol Yetkileri

### Admin
- ✅ Kitap/Yazar/Kategori/Kullanıcı CRUD
- ✅ Tüm işlemleri görüntüleme
- ✅ İstatistikleri görme

### Üye
- ✅ Kitap arama ve görüntüleme
- ✅ Kitap ödünç alma
- ✅ Kendi kitaplarını iade etme
- ✅ Kendi cezalarını ödeme

---

## 📝 Notlar

- Proje çok katmanlı mimari (N-Tier) prensiplerini takip eder
- Her katman sadece altındaki katmanı bilir
- Veritabanı değişikliği sadece Repository katmanını etkiler
- İş mantığı değişikliği sadece Service katmanını etkiler

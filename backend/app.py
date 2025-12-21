"""
Kütüphane Yönetim Sistemi - Ana Uygulama
Çok Katmanlı Mimari: Entity -> Repository -> Service -> Controller
"""

import sys
import os

# Proje kök dizinini Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from config import DatabaseConfig

# Controller'ları import et
from controllers import (
    auth_bp,
    user_bp,
    author_bp,
    category_bp,
    book_bp,
    transaction_bp,
    penalty_bp,
    member_bp,
    stats_bp
)

# Flask uygulaması
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Blueprint'leri kaydet
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(author_bp)
app.register_blueprint(category_bp)
app.register_blueprint(book_bp)
app.register_blueprint(transaction_bp)
app.register_blueprint(penalty_bp)
app.register_blueprint(member_bp)
app.register_blueprint(stats_bp)


@app.route('/')
def index():
    """Ana sayfa"""
    return app.send_static_file('index.html')


if __name__ == '__main__':
    print("=" * 60)
    print("📚 Kütüphane Yönetim Sistemi")
    print("   Çok Katmanlı Mimari (N-Tier Architecture)")
    print("=" * 60)
    print()
    print("📁 Proje Yapısı:")
    print("   ├── entities/      - Veri Modelleri (Entity Layer)")
    print("   ├── repositories/  - Veritabanı İşlemleri (Repository Layer)")
    print("   ├── services/      - İş Mantığı (Service Layer)")
    print("   ├── controllers/   - API Endpoints (Controller Layer)")
    print("   └── static/        - Frontend (View Layer)")
    print()
    
    # Veritabanı bağlantı testi
    success, msg = DatabaseConfig.test_connection()
    if success:
        print(f"✅ Veritabanı: {msg}")
        
        # İstatistikleri göster
        from services.stats_service import stats_service
        stats = stats_service.get_admin_stats()
        print(f"📚 Kitaplar: {stats['totalBooks']}")
        print(f"👥 Kullanıcılar: {stats['totalUsers']}")
        print(f"📋 Aktif Ödünç: {stats['activeBorrows']}")
        print(f"⚠️ Toplam Ceza: {stats['totalPenalties']:.2f} TL")
    else:
        print(f"❌ Veritabanı Hatası: {msg}")
    
    print()
    print("=" * 60)
    print("🌐 Uygulama: http://localhost:5001")
    print("📡 API: http://localhost:5001/api")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)

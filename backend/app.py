"""
APP.PY - Kütüphane Yönetim Sistemi

SQL Server Trigger ve Stored Procedure kullanır:
- sp_BorrowBook: Kitap ödünç alma
- sp_ReturnBook: Kitap iade etme
- sp_PayPenalty: Ceza ödeme
- trg_CalculatePenalty: Otomatik ceza hesaplama

Ceza: 5 TL/dakika, İade süresi: 1 dakika
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from config import DatabaseConfig

from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.author_controller import author_bp
from controllers.category_controller import category_bp
from controllers.book_controller import book_bp
from controllers.transaction_controller import transaction_bp
from controllers.penalty_controller import penalty_bp
from controllers.member_controller import member_bp
from controllers.stats_controller import stats_bp

app = Flask(__name__, static_folder='frontend')
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
    return send_from_directory('frontend', 'index.html')

@app.route('/styles.css')
def styles():
    return send_from_directory('frontend', 'styles.css')

@app.route('/app.js')
def scripts():
    return send_from_directory('frontend', 'app.js')

if __name__ == '__main__':
    print("=" * 60)
    print("KÜTÜPHANE YÖNETİM SİSTEMİ")
    print("=" * 60)
    print()
    print("🔧 SQL Server Bileşenleri:")
    print("   - sp_BorrowBook    : Kitap ödünç alma")
    print("   - sp_ReturnBook    : Kitap iade etme")
    print("   - sp_PayPenalty    : Ceza ödeme")
    print("   - trg_CalculatePenalty : Otomatik ceza (TRIGGER)")
    print()
    print("⏱️ Ceza: 5 TL/dakika | İade süresi: 1 dakika")
    print()
    
    success, message = DatabaseConfig.test_connection()
    print(f"{'✅' if success else '❌'} Veritabanı: {message}")
    
    print()
    print("🔑 Giriş: admin@kutuphane.com / 123456")
    print("         test@test.com / 123456")
    print()
    print("=" * 60)
    print("🌐 http://localhost:5001")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)

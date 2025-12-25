/* APP.JS - Kütüphane Yönetim Sistemi */

const API_URL = 'http://localhost:5001/api';

let token = localStorage.getItem('token');
let currentUser = JSON.parse(localStorage.getItem('user') || 'null');
let editType = '';
let editId = 0;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', () => {
    console.log('Sayfa yüklendi');
    console.log('Token:', token);
    console.log('User:', currentUser);
    
    if (token && currentUser) {
        showMainPage();
    }
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});

// Tab değiştirme
function showTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabs = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    
    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        tabs[0].classList.add('active');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        tabs[1].classList.add('active');
    }
    
    // Mesajı temizle
    const msg = document.getElementById('loginMessage');
    if (msg) msg.classList.add('hidden');
}

// Giriş işlemi
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        console.log('Login response:', data);
        
        if (data.success) {
            token = data.token;
            currentUser = data.user;
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(currentUser));
            showMainPage();
        } else {
            showMessage('loginMessage', data.error, 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('loginMessage', 'Bağlantı hatası: ' + error.message, 'error');
    }
}

// Kayıt işlemi
async function handleRegister(e) {
    e.preventDefault();
    
    const fullName = document.getElementById('registerName').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
    
    // Validasyonlar
    if (!fullName || !email || !password) {
        showMessage('loginMessage', 'Tüm alanları doldurun', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('loginMessage', 'Şifre en az 6 karakter olmalı', 'error');
        return;
    }
    
    if (password !== passwordConfirm) {
        showMessage('loginMessage', 'Şifreler eşleşmiyor', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fullName, email, password })
        });
        
        const data = await response.json();
        console.log('Register response:', data);
        
        if (data.success) {
            showMessage('loginMessage', '✓ Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success');
            // Formu temizle
            document.getElementById('registerName').value = '';
            document.getElementById('registerEmail').value = '';
            document.getElementById('registerPassword').value = '';
            document.getElementById('registerPasswordConfirm').value = '';
            // Giriş tabına geç
            setTimeout(() => showTab('login'), 2000);
        } else {
            showMessage('loginMessage', data.error || 'Kayıt başarısız', 'error');
        }
    } catch (error) {
        console.error('Register error:', error);
        showMessage('loginMessage', 'Bağlantı hatası: ' + error.message, 'error');
    }
}

// Çıkış işlemi
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    token = null;
    currentUser = null;
    
    document.getElementById('loginPage').classList.remove('hidden');
    document.getElementById('mainPage').classList.add('hidden');
    
    const adminPanel = document.getElementById('adminPanel');
    const userPanel = document.getElementById('userPanel');
    if (adminPanel) adminPanel.classList.add('hidden');
    if (userPanel) userPanel.classList.add('hidden');
}

// Ana sayfa
function showMainPage() {
    console.log('showMainPage çağrıldı');
    console.log('currentUser:', currentUser);
    
    if (!currentUser) {
        console.error('currentUser null!');
        return;
    }
    
    document.getElementById('loginPage').classList.add('hidden');
    document.getElementById('mainPage').classList.remove('hidden');
    document.getElementById('userInfo').textContent = `Hoşgeldin, ${currentUser.fullName}`;
    
    const roleEl = document.getElementById('userRole');
    const adminPanel = document.getElementById('adminPanel');
    const userPanel = document.getElementById('userPanel');
    
    console.log('User role:', currentUser.role);
    
    if (currentUser.role === 'admin') {
        console.log('Admin paneli gösteriliyor');
        roleEl.textContent = 'Admin';
        roleEl.className = 'badge badge-warning';
        if (adminPanel) adminPanel.classList.remove('hidden');
        if (userPanel) userPanel.classList.add('hidden');
        loadAdminData();
    } else {
        console.log('Kullanıcı paneli gösteriliyor');
        roleEl.textContent = 'Üye';
        roleEl.className = 'badge badge-success';
        if (adminPanel) adminPanel.classList.add('hidden');
        if (userPanel) userPanel.classList.remove('hidden');
        loadUserData();
    }
}

// ==================== ADMIN FONKSİYONLARI ====================

async function loadAdminData() {
    console.log('Admin verileri yükleniyor...');
    try {
        await loadAuthors();
        await loadCategories();
        await loadAdminBooks();
        await loadAllTransactions();
        await loadAllPenalties();
        await loadAdminStats();
        console.log('Admin verileri yüklendi');
    } catch (error) {
        console.error('Admin veri yükleme hatası:', error);
    }
}

async function loadAdminStats() {
    try {
        const [booksRes, authorsRes, categoriesRes, usersRes] = await Promise.all([
            fetch(`${API_URL}/books`),
            fetch(`${API_URL}/authors`),
            fetch(`${API_URL}/categories`),
            fetch(`${API_URL}/users`)
        ]);
        
        const books = await booksRes.json();
        const authors = await authorsRes.json();
        const categories = await categoriesRes.json();
        const users = await usersRes.json();
        
        const statBooks = document.getElementById('adminStatBooks');
        const statAuthors = document.getElementById('adminStatAuthors');
        const statCategories = document.getElementById('adminStatCategories');
        const statUsers = document.getElementById('adminStatUsers');
        
        if (statBooks) statBooks.textContent = Array.isArray(books) ? books.length : 0;
        if (statAuthors) statAuthors.textContent = Array.isArray(authors) ? authors.length : 0;
        if (statCategories) statCategories.textContent = Array.isArray(categories) ? categories.length : 0;
        if (statUsers) statUsers.textContent = Array.isArray(users) ? users.length : 0;
    } catch (error) {
        console.error('Admin stats yüklenemedi:', error);
    }
}

// YAZAR İŞLEMLERİ
async function loadAuthors() {
    try {
        const response = await fetch(`${API_URL}/authors`);
        const authors = await response.json();
        console.log('Yazarlar:', authors);
        
        const tbody = document.querySelector('#authorsTable tbody');
        if (tbody && Array.isArray(authors)) {
            tbody.innerHTML = authors.map(a => `
                <tr>
                    <td>${a.id}</td>
                    <td>${a.name}</td>
                    <td>${a.lastName}</td>
                    <td>${a.country || ''}</td>
                    <td>
                        <button class="btn btn-small btn-primary" onclick="editAuthor(${a.id}, '${a.name}', '${a.lastName}', '${a.country || ''}')">Düzenle</button>
                        <button class="btn btn-small btn-danger" onclick="deleteAuthor(${a.id})">Sil</button>
                    </td>
                </tr>
            `).join('');
        }
        
        // Select'leri güncelle
        const select = document.getElementById('bookAuthorId');
        if (select && Array.isArray(authors)) {
            select.innerHTML = '<option value="">Yazar Seç</option>' + authors.map(a => `<option value="${a.id}">${a.name} ${a.lastName}</option>`).join('');
        }
    } catch (error) {
        console.error('Yazarlar yüklenemedi:', error);
    }
}

async function addAuthor() {
    const name = document.getElementById('authorName').value;
    const lastName = document.getElementById('authorLastName').value;
    const country = document.getElementById('authorCountry').value;
    
    if (!name || !lastName) {
        showMessage('mainMessage', 'Ad ve soyad gerekli', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/authors`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, lastName, country })
        });
        
        if (response.ok) {
            showMessage('mainMessage', '✓ Yazar eklendi', 'success');
            document.getElementById('authorName').value = '';
            document.getElementById('authorLastName').value = '';
            document.getElementById('authorCountry').value = '';
            loadAuthors();
            loadAdminStats();
        } else {
            const data = await response.json();
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

function editAuthor(id, name, lastName, country) {
    editType = 'author';
    editId = id;
    document.getElementById('modalTitle').textContent = 'Yazar Düzenle';
    document.getElementById('modalBody').innerHTML = `
        <div class="form-group">
            <label>Ad</label>
            <input type="text" id="editName" value="${name}">
        </div>
        <div class="form-group">
            <label>Soyad</label>
            <input type="text" id="editLastName" value="${lastName}">
        </div>
        <div class="form-group">
            <label>Ülke</label>
            <input type="text" id="editCountry" value="${country}">
        </div>
    `;
    document.getElementById('editModal').classList.remove('hidden');
}

async function deleteAuthor(id) {
    if (!confirm('Bu yazarı silmek istediğinize emin misiniz?')) return;
    
    try {
        const response = await fetch(`${API_URL}/authors/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showMessage('mainMessage', '✓ Yazar silindi', 'success');
            loadAuthors();
            loadAdminStats();
        } else {
            const data = await response.json();
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

// KATEGORİ İŞLEMLERİ
async function loadCategories() {
    try {
        const response = await fetch(`${API_URL}/categories`);
        const categories = await response.json();
        console.log('Kategoriler:', categories);
        
        const tbody = document.querySelector('#categoriesTable tbody');
        if (tbody && Array.isArray(categories)) {
            tbody.innerHTML = categories.map(c => `
                <tr>
                    <td>${c.id}</td>
                    <td>${c.name}</td>
                    <td>
                        <button class="btn btn-small btn-primary" onclick="editCategory(${c.id}, '${c.name}')">Düzenle</button>
                        <button class="btn btn-small btn-danger" onclick="deleteCategory(${c.id})">Sil</button>
                    </td>
                </tr>
            `).join('');
        }
        
        // Select'i güncelle
        const select = document.getElementById('bookCategoryId');
        if (select && Array.isArray(categories)) {
            select.innerHTML = '<option value="">Kategori Seç</option>' + categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        }
    } catch (error) {
        console.error('Kategoriler yüklenemedi:', error);
    }
}

async function addCategory() {
    const name = document.getElementById('categoryName').value;
    
    if (!name) {
        showMessage('mainMessage', 'Kategori adı gerekli', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/categories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        
        if (response.ok) {
            showMessage('mainMessage', '✓ Kategori eklendi', 'success');
            document.getElementById('categoryName').value = '';
            loadCategories();
            loadAdminStats();
        } else {
            const data = await response.json();
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

function editCategory(id, name) {
    editType = 'category';
    editId = id;
    document.getElementById('modalTitle').textContent = 'Kategori Düzenle';
    document.getElementById('modalBody').innerHTML = `
        <div class="form-group">
            <label>Kategori Adı</label>
            <input type="text" id="editCategoryName" value="${name}">
        </div>
    `;
    document.getElementById('editModal').classList.remove('hidden');
}

async function deleteCategory(id) {
    if (!confirm('Bu kategoriyi silmek istediğinize emin misiniz?')) return;
    
    try {
        const response = await fetch(`${API_URL}/categories/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showMessage('mainMessage', '✓ Kategori silindi', 'success');
            loadCategories();
            loadAdminStats();
        } else {
            const data = await response.json();
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

// KİTAP İŞLEMLERİ (Admin)
async function loadAdminBooks() {
    try {
        const response = await fetch(`${API_URL}/books`);
        const books = await response.json();
        console.log('Admin kitaplar:', books);
        
        const tbody = document.querySelector('#adminBooksTable tbody');
        if (tbody && Array.isArray(books)) {
            tbody.innerHTML = books.map(b => `
                <tr>
                    <td>${b.id}</td>
                    <td>${b.title}</td>
                    <td>${b.authorName || ''}</td>
                    <td>${b.categoryName || ''}</td>
                    <td>${b.available} / ${b.stockNumber}</td>
                    <td>${b.yearOfPublication || ''}</td>
                    <td>
                        <button class="btn btn-small btn-primary" onclick="editBook(${b.id}, '${b.title.replace(/'/g, "\\'")}', ${b.authorId}, ${b.categoryId}, ${b.stockNumber}, ${b.yearOfPublication || 2024})">Düzenle</button>
                        <button class="btn btn-small btn-danger" onclick="deleteBook(${b.id})">Sil</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Kitaplar yüklenemedi:', error);
    }
}

async function addBook() {
    const title = document.getElementById('bookTitle').value;
    const authorId = document.getElementById('bookAuthorId').value;
    const categoryId = document.getElementById('bookCategoryId').value;
    const stockNumber = document.getElementById('bookStock').value;
    const yearOfPublication = document.getElementById('bookYear').value;
    
    if (!title || !authorId || !categoryId) {
        showMessage('mainMessage', 'Kitap adı, yazar ve kategori gerekli', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/books`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                title, 
                authorId: parseInt(authorId), 
                categoryId: parseInt(categoryId), 
                stockNumber: parseInt(stockNumber) || 1, 
                yearOfPublication: parseInt(yearOfPublication) || 2024 
            })
        });
        
        if (response.ok) {
            showMessage('mainMessage', '✓ Kitap eklendi', 'success');
            document.getElementById('bookTitle').value = '';
            document.getElementById('bookStock').value = '1';
            document.getElementById('bookYear').value = '';
            loadAdminBooks();
            loadAdminStats();
        } else {
            const data = await response.json();
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

function editBook(id, title, authorId, categoryId, stock, year) {
    editType = 'book';
    editId = id;
    document.getElementById('modalTitle').textContent = 'Kitap Düzenle';
    
    const authorSelect = document.getElementById('bookAuthorId');
    const categorySelect = document.getElementById('bookCategoryId');
    
    document.getElementById('modalBody').innerHTML = `
        <div class="form-group">
            <label>Kitap Adı</label>
            <input type="text" id="editBookTitle" value="${title}">
        </div>
        <div class="form-group">
            <label>Yazar</label>
            <select id="editBookAuthorId">${authorSelect ? authorSelect.innerHTML : ''}</select>
        </div>
        <div class="form-group">
            <label>Kategori</label>
            <select id="editBookCategoryId">${categorySelect ? categorySelect.innerHTML : ''}</select>
        </div>
        <div class="form-group">
            <label>Stok</label>
            <input type="number" id="editBookStock" value="${stock}" min="1">
        </div>
        <div class="form-group">
            <label>Yıl</label>
            <input type="number" id="editBookYear" value="${year}">
        </div>
    `;
    
    const editAuthorSelect = document.getElementById('editBookAuthorId');
    const editCategorySelect = document.getElementById('editBookCategoryId');
    if (editAuthorSelect) editAuthorSelect.value = authorId;
    if (editCategorySelect) editCategorySelect.value = categoryId;
    
    document.getElementById('editModal').classList.remove('hidden');
}

async function deleteBook(id) {
    if (!confirm('Bu kitabı silmek istediğinize emin misiniz?')) return;
    
    try {
        const response = await fetch(`${API_URL}/books/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showMessage('mainMessage', '✓ Kitap silindi', 'success');
            loadAdminBooks();
            loadAdminStats();
        } else {
            const data = await response.json();
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

// TÜM İŞLEMLER (Admin)
async function loadAllTransactions() {
    try {
        const response = await fetch(`${API_URL}/transactions`);
        const transactions = await response.json();
        console.log('Tüm işlemler:', transactions);
        
        const tbody = document.querySelector('#allTransactionsTable tbody');
        if (!tbody) return;
        
        if (!Array.isArray(transactions) || transactions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">Henüz işlem yok</td></tr>';
            return;
        }
        
        tbody.innerHTML = transactions.map(tx => `
            <tr>
                <td>${tx.id}</td>
                <td>${tx.userName || ''}</td>
                <td>${tx.bookTitle || ''}</td>
                <td>${tx.borrowDate || ''}</td>
                <td>${tx.returnDate || ''}</td>
                <td>${tx.realReturnDate || '-'}</td>
                <td>
                    <span class="badge ${tx.state === 'İade Edildi' ? 'badge-success' : 'badge-warning'}">
                        ${tx.state || 'Bilinmiyor'}
                    </span>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('İşlemler yüklenemedi:', error);
    }
}

// TÜM CEZALAR (Admin)
async function loadAllPenalties() {
    try {
        const response = await fetch(`${API_URL}/penalties`);
        const penalties = await response.json();
        console.log('Tüm cezalar:', penalties);
        
        const tbody = document.querySelector('#allPenaltiesTable tbody');
        if (!tbody) return;
        
        if (!Array.isArray(penalties) || penalties.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">Ceza yok</td></tr>';
            return;
        }
        
        tbody.innerHTML = penalties.map(p => `
            <tr>
                <td>${p.id}</td>
                <td>${p.userName || ''}</td>
                <td>${p.numberOfDay || 0} dakika</td>
                <td><strong>${p.amount || 0} TL</strong></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Cezalar yüklenemedi:', error);
    }
}

// MODAL KAYDET
async function saveEdit() {
    let url = '';
    let body = {};
    
    if (editType === 'author') {
        url = `${API_URL}/authors/${editId}`;
        body = {
            name: document.getElementById('editName').value,
            lastName: document.getElementById('editLastName').value,
            country: document.getElementById('editCountry').value
        };
    } else if (editType === 'category') {
        url = `${API_URL}/categories/${editId}`;
        body = { name: document.getElementById('editCategoryName').value };
    } else if (editType === 'book') {
        url = `${API_URL}/books/${editId}`;
        body = {
            title: document.getElementById('editBookTitle').value,
            authorId: parseInt(document.getElementById('editBookAuthorId').value),
            categoryId: parseInt(document.getElementById('editBookCategoryId').value),
            stockNumber: parseInt(document.getElementById('editBookStock').value),
            yearOfPublication: parseInt(document.getElementById('editBookYear').value)
        };
    }
    
    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        if (response.ok) {
            showMessage('mainMessage', '✓ Güncellendi', 'success');
            closeModal();
            loadAdminData();
        } else {
            const data = await response.json();
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

function closeModal() {
    document.getElementById('editModal').classList.add('hidden');
}

// ==================== KULLANICI FONKSİYONLARI ====================

async function loadUserData() {
    console.log('Kullanıcı verileri yükleniyor...');
    try {
        await loadBooks();
        await loadMyTransactions();
        await loadMyPenalties();
        await loadStats();
        console.log('Kullanıcı verileri yüklendi');
    } catch (error) {
        console.error('Kullanıcı veri yükleme hatası:', error);
    }
}

async function loadStats() {
    try {
        const statsRes = await fetch(`${API_URL}/my/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const stats = await statsRes.json();
        console.log('Stats:', stats);
        
        const statBorrows = document.getElementById('statBorrows');
        const statPenalties = document.getElementById('statPenalties');
        const statBooks = document.getElementById('statBooks');
        
        if (statBorrows) statBorrows.textContent = stats.activeBorrows || 0;
        if (statPenalties) statPenalties.textContent = (stats.totalPenalties || 0) + ' TL';
        
        const booksRes = await fetch(`${API_URL}/books`);
        const books = await booksRes.json();
        if (statBooks) statBooks.textContent = Array.isArray(books) ? books.length : 0;
    } catch (error) {
        console.error('Stats yüklenemedi:', error);
    }
}

async function loadBooks() {
    try {
        const response = await fetch(`${API_URL}/books`);
        const books = await response.json();
        console.log('Kitaplar:', books);
        
        const tbody = document.querySelector('#booksTable tbody');
        if (!tbody) {
            console.error('#booksTable tbody bulunamadı!');
            return;
        }
        
        if (!Array.isArray(books) || books.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">Kitap yok</td></tr>';
            return;
        }
        
        tbody.innerHTML = books.map(book => `
            <tr>
                <td>${book.title}</td>
                <td>${book.authorName || ''}</td>
                <td>${book.categoryName || ''}</td>
                <td>
                    <span class="badge ${book.available > 0 ? 'badge-success' : 'badge-danger'}">
                        ${book.available} / ${book.stockNumber}
                    </span>
                </td>
                <td>
                    ${book.available > 0 
                        ? `<button class="btn btn-secondary btn-small" onclick="borrowBook(${book.id})">Ödünç Al</button>`
                        : '<span class="badge badge-danger">Stokta Yok</span>'
                    }
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Kitaplar yüklenemedi:', error);
    }
}

async function borrowBook(bookId) {
    try {
        const response = await fetch(`${API_URL}/borrow`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ bookId })
        });
        
        const data = await response.json();
        console.log('Borrow response:', data);
        
        if (data.success) {
            showMessage('mainMessage', '✓ ' + data.message, 'success');
            loadBooks();
            loadMyTransactions();
            loadStats();
        } else {
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

async function loadMyTransactions() {
    try {
        const response = await fetch(`${API_URL}/my/transactions`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const transactions = await response.json();
        console.log('İşlemlerim:', transactions);
        
        const tbody = document.querySelector('#myTransactionsTable tbody');
        if (!tbody) {
            console.error('#myTransactionsTable tbody bulunamadı!');
            return;
        }
        
        if (!Array.isArray(transactions) || transactions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">Henüz işlem yok</td></tr>';
            return;
        }
        
        tbody.innerHTML = transactions.map(tx => `
            <tr>
                <td>${tx.bookTitle || ''}</td>
                <td>${tx.borrowDate || ''}</td>
                <td>${tx.returnDate || ''}</td>
                <td>${tx.realReturnDate || '-'}</td>
                <td>
                    <span class="badge ${tx.state === 'İade Edildi' ? 'badge-success' : 'badge-warning'}">
                        ${tx.state || 'Bilinmiyor'}
                    </span>
                </td>
                <td>
                    ${tx.state !== 'İade Edildi' 
                        ? `<button class="btn btn-primary btn-small" onclick="returnBook(${tx.id})">İade Et</button>`
                        : '-'
                    }
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('İşlemler yüklenemedi:', error);
    }
}

async function returnBook(txId) {
    try {
        const response = await fetch(`${API_URL}/my/transactions/${txId}/return`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        console.log('Return response:', data);
        
        if (data.success) {
            const msgType = data.message.includes('ceza') ? 'error' : 'success';
            const icon = data.message.includes('ceza') ? '⚠️' : '✓';
            showMessage('mainMessage', icon + ' ' + data.message, msgType);
            
            loadBooks();
            loadMyTransactions();
            loadMyPenalties();
            loadStats();
        } else {
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

async function loadMyPenalties() {
    try {
        const response = await fetch(`${API_URL}/my/penalties`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const penalties = await response.json();
        console.log('Cezalarım:', penalties);
        
        const tbody = document.querySelector('#myPenaltiesTable tbody');
        if (!tbody) {
            console.error('#myPenaltiesTable tbody bulunamadı!');
            return;
        }
        
        if (!Array.isArray(penalties) || penalties.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center">Cezanız yok 🎉</td></tr>';
            return;
        }
        
        tbody.innerHTML = penalties.map(p => `
            <tr>
                <td>${p.numberOfDay || 0} dakika gecikme</td>
                <td><strong>${p.amount || 0} TL</strong></td>
                <td>
                    <button class="btn btn-secondary btn-small" onclick="payPenalty(${p.id})">Öde</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Cezalar yüklenemedi:', error);
    }
}

async function payPenalty(penaltyId) {
    try {
        const response = await fetch(`${API_URL}/my/penalties/${penaltyId}/pay`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        console.log('Pay response:', data);
        
        if (data.success) {
            showMessage('mainMessage', '✓ ' + data.message, 'success');
            loadMyPenalties();
            loadStats();
        } else {
            showMessage('mainMessage', '✗ ' + (data.error || 'Hata'), 'error');
        }
    } catch (error) {
        showMessage('mainMessage', 'Hata: ' + error.message, 'error');
    }
}

// Mesaj gösterme
function showMessage(elementId, message, type) {
    const el = document.getElementById(elementId);
    if (!el) {
        console.error(`Element bulunamadı: ${elementId}`);
        return;
    }
    el.className = `message message-${type}`;
    el.textContent = message;
    el.classList.remove('hidden');
    
    setTimeout(() => {
        el.classList.add('hidden');
    }, 5000);
}

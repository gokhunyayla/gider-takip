# Gelir Gider Takip Sistemi

Flask tabanlı, modern ve kullanımı kolay bir gelir-gider takip uygulaması.

## Özellikler

- 📊 Aylık ve yıllık gider takibi
- 👤 Kullanıcı yönetimi ve kimlik doğrulama
- 📈 Dashboard ve görsel raporlar
- 💾 Excel dosyası import/export
- 🎨 Bootstrap 5 ve Tailwind CSS ile modern tasarım
- 🔐 JWT tabanlı API güvenliği

## Gereksinimler

- Python 3.11+
- MariaDB (Production) veya SQLite (Development)

## Kurulum

1. Repoyu klonlayın:
```bash
git clone [repo-url]
cd gelir-gider-tablo
```

2. Sanal ortam oluşturun:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate  # Windows
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. `.env` dosyasını düzenleyin (gerekirse)

5. Uygulamayı başlatın:
```bash
python run.py
```

## Kullanım

Uygulama http://localhost:5021 adresinde çalışacaktır.

### Demo Giriş Bilgileri
- **Kullanıcı:** admin
- **Şifre:** admin123

## Proje Yapısı

```
gelir-gider-tablo/
├── app/
│   ├── models/          # Veritabanı modelleri
│   ├── views/           # Route tanımları
│   ├── controllers/     # İş mantığı
│   ├── static/          # CSS, JS dosyaları
│   └── templates/       # HTML şablonları
├── config/              # Yapılandırma dosyaları
├── sources/             # Excel dosyaları
├── .env                 # Ortam değişkenleri
├── requirements.txt     # Python bağımlılıkları
└── run.py              # Uygulama başlatıcı
```

## API Endpoints

- `POST /auth/api/login` - Kullanıcı girişi
- `GET /api/categories` - Kategori listesi
- `GET /api/expenses` - Gider listesi
- `POST /api/expenses` - Yeni gider ekle
- `GET /api/reports/summary` - Özet rapor

## Gider Kategorileri

Uygulama Excel dosyasındaki 33 farklı gider kategorisini destekler:
- Kira, Personel Maaşları, SGK
- Faturalar (Elektrik, İnternet, Telefon)
- Kargo ve Lojistik
- Ofis Giderleri
- ve daha fazlası...

## Demo Excel Dosyası

`sources/demo-gelir-gider.xlsx` dosyası örnek veriler içerir.
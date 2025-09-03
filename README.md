# 📊 TCMB EVDS Kur Çekme Aracı

Bu proje, **TCMB EVDS API** üzerinden günlük **USD, EUR ve GBP** döviz kurlarını çekip SQL Server veritabanındaki `AL_Doviz` tablosuna kaydeder.

- Son **4 günün verisini** çeker  
- Hafta sonu / tatil günleri için önceki değeri otomatik olarak doldurur (forward-fill)  
- `AL_Doviz` tablosuna yalnızca **daha önce eklenmemiş** satırları ekler  

---

## Gereksinimler

- Python 3.10+ (örnek: 3.13)
- SQL Server (önceden oluşturulmuş tablo):


# Veritabanı Şeması (Önerilen)

Eğer tablon yoksa şu şemayla oluşturabilirsin. TARIH üzerinde PRIMARY KEY olduğundan tekrar kayıt engellenir.
```
CREATE TABLE dbo.AL_Doviz (
    TARIH     date        NOT NULL PRIMARY KEY,
    USD       decimal(18,4) NULL,
    EURO      decimal(18,4) NULL,
    STERLIN   decimal(18,4) NULL,
);
```
# Kurulum

Önce gitten bu projeyi klonlayın.
Sonra Pythonla bir virtual environment yaratın ve requirements.txt'nin içindeki gerekli kütüphaneleri indirin.
```
git clone https://github.com/degthecoder/TCMB-EVDS-KUR-CEKME
cd KurCekme
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows PowerShell:
# .\venv\Scripts\Activate.ps1
```

# Yapılandırma

Proje klasörüne .env dosyası ekleyin:
```
DB_HOST=sqlserver-adresi
DB_NAME=veritabani_adi
DB_USER=kullanici
DB_PASSWORD=sifre
API_KEY=evds_api_anahtari
```

# Sorgu Mantığı
.env dosaysı indirdikten sonra {Your_Table_Name} yazan kısımlara kendi Microsoft SQL Server database isminizi yazın.
```
query = text("""
    IF NOT EXISTS (SELECT 1 FROM {YOUR_TABLE_NAME} WHERE TARIH = :tarih)
    BEGIN
        INSERT INTO {YOUR_TABLE_NAME} (TARIH, USD, EURO, STERLIN)
        VALUES (:tarih, :usd, :euro, :sterlin)
    END
    """)
```

Buradaki query sadece olmayan satırları eklemek için tasarlanmıştır, eğer güncelleme de yapmak istiyorsanız bu sorguyu değiştirebilirsiniz.

# Çalıştırma
source venv/bin/activate
python3 kur_job.py

Örnek çıktı:
```
DB: sa@localhost/DovizDB
       Tarih     usd    euro  sterlin
0 2025-08-29  41.04   47.83   55.53
1 2025-08-30  41.04   47.83   55.53
...
Bitti. 6 gün işlendi (yeni olanlar eklendi).

```

# Notlar

Notlar

Kullanılan EVDS serileri:

TP.DK.USD.S.YTL → USD satış

TP.DK.EUR.S.YTL → EUR satış

TP.DK.GBP.S.YTL → GBP satış

Hafta sonu / tatil günlerinde veri bulunmazsa son geçerli değerle doldurulur.

AL_Doviz.TARIH üzerinde PRIMARY KEY bulunduğu için tekrar eden satırlar eklenmez.

Eğer MSSQL kullanmıyorsanız, sorguyu (INSERT, MERGE vb.) ve SQLAlchemy bağlantı ayarlarını değiştirerek kendi kullandığınız veritabanına (PostgreSQL, MySQL/MariaDB, SQLite vb.) bağlanabilirsiniz.

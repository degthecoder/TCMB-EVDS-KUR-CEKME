# 📊 TCMB EVDS Kur Çekme Aracı

Bu proje, **TCMB EVDS API** üzerinden günlük **USD, EUR ve GBP** döviz kurlarını çekip SQL Server veritabanındaki `AL_Doviz` tablosuna kaydeder.

- Son **4 günün verisini** çeker  
- Hafta sonu / tatil günleri için önceki değeri otomatik olarak doldurur (forward-fill)  
- `AL_Doviz` tablosuna yalnızca **daha önce eklenmemiş** satırları ekler  

---

## ⚙️ Gereksinimler

- Python 3.10+ (örnek: 3.13)
- SQL Server (önceden oluşturulmuş tablo):

# 📥 Kurulum
```
git clone <bu-repo>
cd KurCekme
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


# 🔑 Yapılandırma

Proje klasörüne .env dosyası ekleyin:
```
DB_HOST=sqlserver-adresi
DB_NAME=veritabani_adi
DB_USER=kullanici
DB_PASSWORD=sifre
API_KEY=evds_api_anahtari
```

# ▶️ Çalıştırma
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

# 📝 Notlar

Kullanılan EVDS serileri:

TP.DK.USD.S.YTL → USD satış

TP.DK.EUR.S.YTL → EUR satış

TP.DK.GBP.S.YTL → GBP satış

Hafta sonu / tatil günlerinde veri bulunmazsa son geçerli değerle doldurulur.

AL_Doviz.TARIH üzerinde PRIMARY KEY bulunduğu için tekrar eden satırlar eklenmez.



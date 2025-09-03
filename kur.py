import sys
import os 
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from evds import evdsAPI

load_dotenv()

def get_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"Missing env var: {name}", file=sys.stderr)
        sys.exit(1)
    return v

def fmt_dmy(d: datetime) -> str:
    return d.strftime("%d-%m-%Y")

def main(  ):
    DB_HOST = get_env("DB_HOST")
    DB_NAME = get_env("DB_NAME")
    DB_USER = get_env("DB_USER")
    DB_PASS = get_env("DB_PASSWORD")
    key = get_env("API_KEY")
    
    print(f"DB: {DB_USER}@{DB_HOST}/{DB_NAME}, API_KEY: {key}")
    
    evds = evdsAPI(key)
    
    tz = ZoneInfo("Europe/Istanbul")
    today = datetime.now(tz).date()
    start_date = today - timedelta(days=5) 
    end_date = today
    
    start_dmy = fmt_dmy(datetime.combine(start_date, datetime.min.time()))
    end_dmy   = fmt_dmy(datetime.combine(end_date,   datetime.min.time()))

    usd_try = evds.get_data(["TP.DK.USD.S.YTL"], startdate=start_dmy, enddate=end_dmy)
    eur_try = evds.get_data(["TP.DK.EUR.S.YTL"], startdate=start_dmy, enddate=end_dmy)
    str_try = evds.get_data(["TP.DK.GBP.S.YTL"], startdate=start_dmy, enddate=end_dmy)
  
    usd_try = usd_try.rename(columns={"TP_DK_USD_S_YTL": "usd"})
    eur_try = eur_try.rename(columns={"TP_DK_EUR_S_YTL": "euro"})
    str_try = str_try.rename(columns={"TP_DK_GBP_S_YTL": "sterlin"})

    usd_try = usd_try.ffill()
    eur_try = eur_try.ffill()
    str_try = str_try.ffill()
    
    kurlar = usd_try.merge(eur_try, on="Tarih").merge(str_try, on="Tarih")
    
    # Make sure Tarih is real datetime (not string)
    kurlar["Tarih"] = pd.to_datetime(kurlar["Tarih"], dayfirst=True).dt.tz_localize(None)

    if kurlar.empty:
        print("EVDS: Son 4 gün için veri yok.")
        return
    
    print(kurlar["Tarih"].dtype)  # should be datetime64[ns]
    print(kurlar.head(10))    

    conn_str = f"mssql+pymssql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    engine = create_engine(conn_str)

    query = text("""
    IF NOT EXISTS (SELECT 1 FROM {YOUR_TABLE_NAME} WHERE TARIH = :tarih)
    BEGIN
        INSERT INTO {YOUR_TABLE_NAME} (TARIH, USD, EURO, STERLIN)
        VALUES (:tarih, :usd, :euro, :sterlin)
    END
    """)

    inserted = 0
    with engine.begin() as conn:
        for r in kurlar.itertuples(index=False):
            tarih = r.Tarih  # convert to date only
            params = {
                "tarih": tarih,
                "usd":   None if "usd" not in kurlar.columns else (None if pd.isna(getattr(r,"usd", None)) else float(r.usd)),
                "euro":  None if "euro" not in kurlar.columns else (None if pd.isna(getattr(r,"euro", None)) else float(r.euro)),
                "sterlin": None if "sterlin" not in kurlar.columns else (None if pd.isna(getattr(r,"sterlin", None)) else float(r.sterlin)),
            }
            res = conn.execute(query, params)
            inserted += 1  # denemek istersen önce var mı kontrol edebilirsin
            
            
    print(f"Bitti. {len(kurlar)} gün işlendi (yeni olanlar eklendi). {inserted} satır eklendi.")
    
if __name__ == "__main__":
    main()
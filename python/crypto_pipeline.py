#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sqlite3

conn = sqlite3.connect("crypto_analytics.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS crypto_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc TEXT,
    coin TEXT,
    price_usd REAL,
    price_inr REAL,
    market_cap_usd REAL,
    vol_24h_usd REAL,
    change_24h_usd_pct REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS fear_greed_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc TEXT,
    fng_value INTEGER,
    fng_classification TEXT
)
""")

conn.commit()
print("Tables created")


# In[2]:


import requests
from datetime import datetime

def fetch_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd,inr",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }

    for attempt in range(1, 6):  # try 5 times
        r = requests.get(url, params=params, timeout=15)

        if r.status_code == 429:
            wait = attempt * 10
            print(f"⚠️ Rate limit hit (429). Waiting {wait}s then retrying...")
            time.sleep(wait)
            continue

        r.raise_for_status()
        return r.json()

    raise Exception("❌ CoinGecko API rate limit: retries exhausted")

def fetch_fear_greed():
    url = "https://api.alternative.me/fng/"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

def ingest_once_sql():
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    prices = fetch_crypto_prices()
    sentiment = fetch_fear_greed()

    # insert prices
    for coin in ["bitcoin", "ethereum"]:
        cur.execute("""
        INSERT INTO crypto_prices(timestamp_utc, coin, price_usd, price_inr, market_cap_usd, vol_24h_usd, change_24h_usd_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ts,
            coin,
            prices[coin].get("usd"),
            prices[coin].get("inr"),
            prices[coin].get("usd_market_cap"),
            prices[coin].get("usd_24h_vol"),
            prices[coin].get("usd_24h_change")
        ))

    # sentiment insert
    fng = sentiment["data"][0]
    cur.execute("""
    INSERT INTO fear_greed_index(timestamp_utc, fng_value, fng_classification)
    VALUES (?, ?, ?)
    """, (
        ts,
        int(fng["value"]),
        fng["value_classification"]
    ))

    conn.commit()
    print(f"Inserted at {ts}")

ingest_once_sql()


# In[3]:


import time

N_RUNS = 3
SLEEP_SECONDS = 10   #  300 

for i in range(1, N_RUNS + 1):
    print(f"\n Run {i}/{N_RUNS}")
    try:
        ingest_once_sql()
    except Exception as e:
        print(" Error:", e)

    if i < N_RUNS:
        print(f" Sleeping {SLEEP_SECONDS} seconds...")
        time.sleep(SLEEP_SECONDS)

print("\n Finished runs")


# In[4]:


import pandas as pd

prices_df = pd.read_sql_query("SELECT * FROM crypto_prices", conn)
sentiment_df = pd.read_sql_query("SELECT * FROM fear_greed_index", conn)

print(prices_df.shape, sentiment_df.shape)
prices_df.tail()


# In[5]:


get_ipython().system('pip install mysql-connector-python pandas requests')


# In[6]:


import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Oscar_mishra@29",
    database="crypto_intelligence"
)

cursor = conn.cursor()
print("Connected to MySQL successfully")


# In[8]:


import requests
from datetime import datetime, timezone

def fetch_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd,inr",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }
    r = requests.get(url, params=params, timeout=15)

    # Optional: show rate limit issue clearly
    if r.status_code == 429:
        raise Exception("⚠️ CoinGecko Rate Limit (429). Wait 1–2 minutes and try again.")

    r.raise_for_status()
    return r.json()

def fetch_fear_greed():
    url = "https://api.alternative.me/fng/"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

def ingest_once_mysql():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    prices = fetch_crypto_prices()
    fng = fetch_fear_greed()["data"][0]

    # Insert Fear & Greed index
    cursor.execute("""
        INSERT IGNORE INTO fear_greed_index(timestamp_utc, fng_value, fng_classification)
        VALUES (%s, %s, %s)
    """, (ts, int(fng["value"]), fng["value_classification"]))

    # Insert BTC & ETH prices
    for coin in ["bitcoin", "ethereum"]:
        cursor.execute("""
            INSERT IGNORE INTO crypto_prices(
                timestamp_utc, coin, price_usd, price_inr, market_cap_usd, vol_24h_usd, change_24h_usd_pct
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            ts,
            coin,
            prices[coin].get("usd"),
            prices[coin].get("inr"),
            prices[coin].get("usd_market_cap"),
            prices[coin].get("usd_24h_vol"),
            prices[coin].get("usd_24h_change")
        ))

    conn.commit()
    print(f"✅ Inserted live data at {ts}")

# Test run
ingest_once_mysql()


# In[9]:


def generate_alerts():
    # latest sentiment
    cursor.execute("""
        SELECT timestamp_utc, fng_value, fng_classification
        FROM fear_greed_index
        ORDER BY timestamp_utc DESC
        LIMIT 1
    """)
    s_ts, fng_value, fng_class = cursor.fetchone()

    # latest prices
    cursor.execute("""
        SELECT timestamp_utc, coin, price_usd, change_24h_usd_pct
        FROM crypto_prices
        WHERE timestamp_utc = %s
    """, (s_ts,))
    rows = cursor.fetchall()

    for ts, coin, price_usd, change_24h in rows:
        # basic risk zone
        if fng_value <= 25:
            risk_zone = "HIGH"
            trade_signal = "BUY"
            reason = "Extreme Fear detected → possible rebound zone"
        elif fng_value >= 75:
            risk_zone = "HIGH"
            trade_signal = "SELL"
            reason = "Extreme Greed detected → possible correction risk"
        else:
            risk_zone = "MED"
            trade_signal = "HOLD"
            reason = "Neutral sentiment → no strong trade_signal"

        cursor.execute("""
            INSERT INTO market_alerts(
                timestamp_utc, coin, trade_signal, risk_zone, reason,
                price_usd, fng_value, fng_classification
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (ts, coin, trade_signal, risk_zone, reason, price_usd, fng_value, fng_class))

    conn.commit()
    print("Alerts generated")

generate_alerts()


# In[10]:


import time

N_RUNS = 12
SLEEP_SECONDS = 300  # after testing make 300

for i in range(1, N_RUNS + 1):
    print(f"\n🚀 Run {i}/{N_RUNS}")
    ingest_once_mysql()
    generate_alerts()

    if i < N_RUNS:
        print(f"⏳ Sleeping {SLEEP_SECONDS} seconds...")
        time.sleep(SLEEP_SECONDS)

print("\n✅ Finished live data collection runs")


# In[ ]:


import pandas as pd

df_prices = pd.read_sql("SELECT * FROM crypto_prices ORDER BY timestamp_utc DESC LIMIT 10", conn)
df_fng = pd.read_sql("SELECT * FROM fear_greed_index ORDER BY timestamp_utc DESC LIMIT 10", conn)
df_alerts = pd.read_sql("SELECT * FROM market_alerts ORDER BY timestamp_utc DESC LIMIT 10", conn)

display(df_prices)
display(df_fng)
display(df_alerts)


# In[ ]:


print("working")


# In[ ]:





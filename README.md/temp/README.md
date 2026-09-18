# 🚀 Crypto Market Intelligence Dashboard (Real-Time)

A real-time crypto analytics pipeline that fetches **live Bitcoin & Ethereum market data** and the **Fear & Greed Index**, stores it in **MySQL**, generates **trade alerts (BUY/SELL/HOLD)**, and visualizes everything in a premium **Power BI dashboard**.

--

## 📌 Features
✅ Live API ingestion (CoinGecko + Alternative.me)  
✅ Stores structured data in **MySQL**  
✅ Generates automated **Market Alerts** using rule-based logic  
✅ Power BI dashboard with KPI cards + trend chart + sentiment gauge + alerts table  
✅ Fully refreshable dashboard (MySQL → Power BI via ODBC)

---

## 🧰 Tech Stack
- **Python** (requests, mysql-connector)
- **MySQL**
- **Power BI**
- **ODBC Driver (MySQL)**

---




---

## 🏗️ Data Pipeline Workflow
1. Fetch live prices of **Bitcoin + Ethereum**
2. Fetch **Fear & Greed Index**
3. Store raw data into MySQL tables:
   - `crypto_prices`
   - `fear_greed_index`
4. Generate alerts into:
   - `market_alerts`
5. Create dashboard-ready views:
   - `vw_market_dashboard`
   - `vw_latest_alerts`
6. Visualize in Power BI

---

## 🗄️ Database Schema
Run these SQL files in MySQL Workbench:


sql/create_tables.sql
sql/views.sql
▶️ How to Run the Project
1️⃣ Setup MySQL
Create the database + tables:

SOURCE sql/create_tables.sql;
SOURCE sql/views.sql;
2️⃣ Run Python Pipeline
Run the script:

python python/pipeline_mysql.py
3️⃣ Open Power BI Dashboard
Open:

powerbi/Crypto_Dashboard.pbix
Click ✅ Refresh to load latest MySQL data.

⏱️ Real-Time Data Collection
You can configure frequency using:

SLEEP_SECONDS = 30 (testing)

SLEEP_SECONDS = 300 (real-time production style)

📌 Resume Highlights
Built a real-time crypto data pipeline using Python + MySQL

Designed a premium Power BI dashboard for sentiment + market monitoring

Implemented automated alert system using Fear & Greed Index + price change logic

Connected Power BI with MySQL using ODBC for live refresh

👤 Author
Shashwat Mishra


---

✅ Save this as: **README.md** in your main project folder  
Then push to GitHub using:

Move README out of folder

```bash
git add README.md
git commit -m "Add README"
git push

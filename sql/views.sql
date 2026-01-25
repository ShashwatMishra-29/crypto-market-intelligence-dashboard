USE crypto_intelligence;

-- View for dashboard (prices + sentiment)
CREATE OR REPLACE VIEW vw_market_dashboard AS
SELECT 
    p.timestamp_utc,
    p.coin,
    p.price_usd,
    p.price_inr,
    p.market_cap_usd,
    p.vol_24h_usd,
    p.change_24h_usd_pct,
    f.fng_value,
    f.fng_classification
FROM crypto_prices p
JOIN fear_greed_index f
    ON p.timestamp_utc = f.timestamp_utc;

-- View for alerts
CREATE OR REPLACE VIEW vw_latest_alerts AS
SELECT *
FROM market_alerts
ORDER BY timestamp_utc DESC;

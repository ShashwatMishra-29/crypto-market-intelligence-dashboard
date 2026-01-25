CREATE DATABASE IF NOT EXISTS crypto_intelligence;
USE crypto_intelligence;

CREATE TABLE IF NOT EXISTS crypto_prices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp_utc DATETIME NOT NULL,
    coin VARCHAR(20) NOT NULL,
    price_usd DOUBLE,
    price_inr DOUBLE,
    market_cap_usd DOUBLE,
    vol_24h_usd DOUBLE,
    change_24h_usd_pct DOUBLE,
    UNIQUE KEY uniq_price (timestamp_utc, coin)
);

CREATE TABLE IF NOT EXISTS fear_greed_index (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp_utc DATETIME NOT NULL,
    fng_value INT,
    fng_classification VARCHAR(30),
    UNIQUE KEY uniq_fng (timestamp_utc)
);

CREATE TABLE IF NOT EXISTS market_alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,fear_greed_index
    timestamp_utc DATETIME NOT NULL,
    coin VARCHAR(20) NOT NULL,
    trade_signal VARCHAR(10) NOT NULL,
    risk_zone VARCHAR(10) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    price_usd DOUBLE,
    fng_value INT,
    fng_classification VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
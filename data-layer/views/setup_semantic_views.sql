-- =====================================================
-- DIA v2.0 - Semantic Views Setup
-- =====================================================
-- Purpose: Create semantic views for SFMC email performance data
-- These views provide a clean, standardized interface for Cortex Analyst
-- Source table: PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.V_FACT_SFMC_SEND_PERFORMANCE_TRACKING
-- Columns: BUSINESSUNIT, SENDID, SENDID_COUNTRY_SK, SENDDATE, SENDS, BOUNCES,
--          UNSUBSCRIBES, OPENS, UNIQUEOPENS, CLICKS, UNIQUECLICKS

USE DATABASE PLAYGROUND_LM;
USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;
USE WAREHOUSE TEST;

-- =====================================================
-- View 1: VW_SFMC_EMAIL_PERFORMANCE
-- =====================================================
-- Row-level email performance with calculated KPIs
-- One row per SENDID x BUSINESSUNIT (same grain as source table)
-- EMAILS_DELIVERED = SENDS - BOUNCES (no dedicated delivered column in source)
-- UNIQUEOPENS / UNIQUECLICKS preferred over raw counts (robust to Apple MPP)

CREATE OR REPLACE VIEW VW_SFMC_EMAIL_PERFORMANCE AS
SELECT
    -- Time dimensions
    t.SENDDATE                                                  AS SEND_DATE,
    YEAR(t.SENDDATE)                                            AS SEND_YEAR,
    MONTH(t.SENDDATE)                                           AS SEND_MONTH,
    'Q' || QUARTER(t.SENDDATE)                                  AS SEND_QUARTER,
    TO_VARCHAR(t.SENDDATE, 'YYYY-MM')                           AS SEND_YEAR_MONTH,

    -- Geographic dimensions
    t.BUSINESSUNIT                                              AS MARKET,

    -- Campaign dimensions
    t.SENDID                                                    AS CAMPAIGN_ID,
    t.SENDID_COUNTRY_SK                                         AS CAMPAIGN_KEY,

    -- Raw volume metrics
    t.SENDS                                                     AS EMAILS_SENT,
    GREATEST(t.SENDS - t.BOUNCES, 0)                            AS EMAILS_DELIVERED,
    t.UNIQUEOPENS                                               AS EMAILS_OPENED,
    t.UNIQUECLICKS                                              AS EMAILS_CLICKED,
    t.BOUNCES                                                   AS EMAILS_BOUNCED,
    t.UNSUBSCRIBES                                              AS EMAILS_UNSUBSCRIBED,

    -- Calculated KPIs
    -- COALESCE + GREATEST guards prevent NULL propagation and divide-by-zero
    ROUND(CASE WHEN COALESCE(t.SENDS, 0) > 0
        THEN (GREATEST(t.SENDS - t.BOUNCES, 0)::FLOAT / t.SENDS) * 100
        ELSE 0 END, 2)                                          AS DELIVERY_RATE,
    ROUND(CASE WHEN GREATEST(t.SENDS - t.BOUNCES, 0) > 0
        THEN (COALESCE(t.UNIQUEOPENS, 0)::FLOAT / GREATEST(t.SENDS - t.BOUNCES, 1)) * 100
        ELSE 0 END, 2)                                          AS OPEN_RATE,
    ROUND(CASE WHEN GREATEST(t.SENDS - t.BOUNCES, 0) > 0
        THEN (COALESCE(t.UNIQUECLICKS, 0)::FLOAT / GREATEST(t.SENDS - t.BOUNCES, 1)) * 100
        ELSE 0 END, 2)                                          AS CLICK_RATE,
    ROUND(CASE WHEN COALESCE(t.UNIQUEOPENS, 0) > 0
        THEN (COALESCE(t.UNIQUECLICKS, 0)::FLOAT / t.UNIQUEOPENS) * 100
        ELSE 0 END, 2)                                          AS CLICK_TO_OPEN_RATE,
    ROUND(CASE WHEN COALESCE(t.SENDS, 0) > 0
        THEN (COALESCE(t.BOUNCES, 0)::FLOAT / t.SENDS) * 100
        ELSE 0 END, 2)                                          AS BOUNCE_RATE,
    ROUND(CASE WHEN GREATEST(t.SENDS - t.BOUNCES, 0) > 0
        THEN (COALESCE(t.UNSUBSCRIBES, 0)::FLOAT / GREATEST(t.SENDS - t.BOUNCES, 1)) * 100
        ELSE 0 END, 2)                                          AS UNSUBSCRIBE_RATE,

    -- Metadata
    CURRENT_TIMESTAMP()                                         AS LAST_UPDATED_TIMESTAMP

FROM PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.V_FACT_SFMC_SEND_PERFORMANCE_TRACKING t

WHERE t.SENDS > 0;

-- =====================================================
-- View 2: VW_CAMPAIGN_SUMMARY
-- =====================================================
-- Campaign-level rollup (aggregated by CAMPAIGN_ID + MARKET)

CREATE OR REPLACE VIEW VW_CAMPAIGN_SUMMARY AS
SELECT
    CAMPAIGN_ID,
    CAMPAIGN_KEY,
    MARKET,
    COUNT(DISTINCT SEND_DATE)           AS TOTAL_SEND_DAYS,
    SUM(EMAILS_SENT)                    AS TOTAL_EMAILS_SENT,
    SUM(EMAILS_DELIVERED)               AS TOTAL_EMAILS_DELIVERED,
    SUM(EMAILS_OPENED)                  AS TOTAL_EMAILS_OPENED,
    SUM(EMAILS_CLICKED)                 AS TOTAL_EMAILS_CLICKED,
    SUM(EMAILS_BOUNCED)                 AS TOTAL_EMAILS_BOUNCED,
    SUM(EMAILS_UNSUBSCRIBED)            AS TOTAL_EMAILS_UNSUBSCRIBED,
    ROUND(AVG(OPEN_RATE), 2)            AS AVG_OPEN_RATE,
    ROUND(AVG(CLICK_RATE), 2)           AS AVG_CLICK_RATE,
    ROUND(AVG(BOUNCE_RATE), 2)          AS AVG_BOUNCE_RATE,
    MIN(SEND_DATE)                      AS FIRST_SEND_DATE,
    MAX(SEND_DATE)                      AS LAST_SEND_DATE
FROM VW_SFMC_EMAIL_PERFORMANCE
GROUP BY CAMPAIGN_ID, CAMPAIGN_KEY, MARKET;

-- =====================================================
-- View 3: VW_MARKET_PERFORMANCE
-- =====================================================
-- Market-level performance aggregation by year/quarter/month

CREATE OR REPLACE VIEW VW_MARKET_PERFORMANCE AS
SELECT
    SEND_YEAR,
    SEND_QUARTER,
    SEND_YEAR_MONTH,
    MARKET,
    COUNT(DISTINCT CAMPAIGN_ID)         AS TOTAL_CAMPAIGNS,
    SUM(EMAILS_SENT)                    AS TOTAL_EMAILS_SENT,
    SUM(EMAILS_DELIVERED)               AS TOTAL_EMAILS_DELIVERED,
    SUM(EMAILS_OPENED)                  AS TOTAL_EMAILS_OPENED,
    SUM(EMAILS_CLICKED)                 AS TOTAL_EMAILS_CLICKED,
    ROUND(AVG(OPEN_RATE), 2)            AS AVG_OPEN_RATE,
    ROUND(AVG(CLICK_RATE), 2)           AS AVG_CLICK_RATE,
    ROUND(AVG(BOUNCE_RATE), 2)          AS AVG_BOUNCE_RATE,
    ROUND(AVG(UNSUBSCRIBE_RATE), 2)     AS AVG_UNSUBSCRIBE_RATE
FROM VW_SFMC_EMAIL_PERFORMANCE
GROUP BY SEND_YEAR, SEND_QUARTER, SEND_YEAR_MONTH, MARKET;

-- =====================================================
-- Verification Queries
-- =====================================================

SHOW VIEWS LIKE 'VW_%' IN SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;

SELECT 'VW_SFMC_EMAIL_PERFORMANCE' AS VIEW_NAME, COUNT(*) AS ROW_COUNT FROM VW_SFMC_EMAIL_PERFORMANCE
UNION ALL
SELECT 'VW_CAMPAIGN_SUMMARY', COUNT(*) FROM VW_CAMPAIGN_SUMMARY
UNION ALL
SELECT 'VW_MARKET_PERFORMANCE', COUNT(*) FROM VW_MARKET_PERFORMANCE;

SELECT * FROM VW_SFMC_EMAIL_PERFORMANCE LIMIT 5;
SELECT * FROM VW_CAMPAIGN_SUMMARY LIMIT 5;
SELECT * FROM VW_MARKET_PERFORMANCE LIMIT 5;

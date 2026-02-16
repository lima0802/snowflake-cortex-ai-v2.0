-- =====================================================
-- DIA v2.0 - Semantic Views Setup
-- =====================================================
-- Purpose: Create semantic views for SFMC email performance data
-- These views provide a clean, standardized interface for Cortex Analyst

USE DATABASE PLAYGROUND_LM;
USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;
USE WAREHOUSE TEST;

-- =====================================================
-- View 1: VW_SFMC_EMAIL_PERFORMANCE
-- =====================================================
-- Aggregated email performance metrics

CREATE OR REPLACE VIEW VW_SFMC_EMAIL_PERFORMANCE AS
SELECT
    -- Time dimensions
    SEND_DATE,
    EXTRACT(YEAR FROM SEND_DATE) AS SEND_YEAR,
    EXTRACT(MONTH FROM SEND_DATE) AS SEND_MONTH,
    EXTRACT(QUARTER FROM SEND_DATE) AS SEND_QUARTER,
    TO_VARCHAR(SEND_DATE, 'YYYY-MM') AS SEND_YEAR_MONTH,

    -- Geographic dimensions
    MARKET,
    COUNTRY,
    REGION,

    -- Campaign dimensions
    CAMPAIGN_NAME,
    CAMPAIGN_TYPE,
    PRODUCT_LINE,

    -- Performance metrics
    EMAILS_SENT,
    EMAILS_DELIVERED,
    EMAILS_OPENED,
    EMAILS_CLICKED,
    EMAILS_BOUNCED,
    EMAILS_UNSUBSCRIBED,

    -- Calculated KPIs
    ROUND(CASE WHEN EMAILS_SENT > 0 THEN (EMAILS_DELIVERED::FLOAT / EMAILS_SENT) * 100 ELSE 0 END, 2) AS DELIVERY_RATE,
    ROUND(CASE WHEN EMAILS_DELIVERED > 0 THEN (EMAILS_OPENED::FLOAT / EMAILS_DELIVERED) * 100 ELSE 0 END, 2) AS OPEN_RATE,
    ROUND(CASE WHEN EMAILS_DELIVERED > 0 THEN (EMAILS_CLICKED::FLOAT / EMAILS_DELIVERED) * 100 ELSE 0 END, 2) AS CLICK_RATE,
    ROUND(CASE WHEN EMAILS_OPENED > 0 THEN (EMAILS_CLICKED::FLOAT / EMAILS_OPENED) * 100 ELSE 0 END, 2) AS CLICK_TO_OPEN_RATE,
    ROUND(CASE WHEN EMAILS_SENT > 0 THEN (EMAILS_BOUNCED::FLOAT / EMAILS_SENT) * 100 ELSE 0 END, 2) AS BOUNCE_RATE,
    ROUND(CASE WHEN EMAILS_DELIVERED > 0 THEN (EMAILS_UNSUBSCRIBED::FLOAT / EMAILS_DELIVERED) * 100 ELSE 0 END, 2) AS UNSUBSCRIBE_RATE,

    -- Metadata
    LAST_UPDATED_TIMESTAMP
FROM
    -- ====================================================
    -- PLACEHOLDER: Replace with your actual SFMC data source
    -- Example: DEV_MARCOM_DB.SFMC_DATA.EMAIL_PERFORMANCE
    -- ====================================================
    (
        -- Sample data for testing (replace with your actual table)
        SELECT
            CURRENT_DATE() AS SEND_DATE,
            'SWEDEN' AS MARKET,
            'SE' AS COUNTRY,
            'EMEA' AS REGION,
            'EX30 Launch Campaign' AS CAMPAIGN_NAME,
            'Product Launch' AS CAMPAIGN_TYPE,
            'EX30' AS PRODUCT_LINE,
            10000 AS EMAILS_SENT,
            9800 AS EMAILS_DELIVERED,
            2450 AS EMAILS_OPENED,
            490 AS EMAILS_CLICKED,
            200 AS EMAILS_BOUNCED,
            10 AS EMAILS_UNSUBSCRIBED,
            CURRENT_TIMESTAMP() AS LAST_UPDATED_TIMESTAMP

        UNION ALL

        SELECT
            CURRENT_DATE() - 30 AS SEND_DATE,
            'GERMANY' AS MARKET,
            'DE' AS COUNTRY,
            'EMEA' AS REGION,
            'XC90 Newsletter' AS CAMPAIGN_NAME,
            'Newsletter' AS CAMPAIGN_TYPE,
            'XC90' AS PRODUCT_LINE,
            15000 AS EMAILS_SENT,
            14700 AS EMAILS_DELIVERED,
            3675 AS EMAILS_OPENED,
            735 AS EMAILS_CLICKED,
            300 AS EMAILS_BOUNCED,
            15 AS EMAILS_UNSUBSCRIBED,
            CURRENT_TIMESTAMP() AS LAST_UPDATED_TIMESTAMP

        UNION ALL

        SELECT
            CURRENT_DATE() - 60 AS SEND_DATE,
            'SPAIN' AS MARKET,
            'ES' AS COUNTRY,
            'EMEA' AS REGION,
            'C40 Test Drive' AS CAMPAIGN_NAME,
            'Engagement' AS CAMPAIGN_TYPE,
            'C40' AS PRODUCT_LINE,
            12000 AS EMAILS_SENT,
            11760 AS EMAILS_DELIVERED,
            2940 AS EMAILS_OPENED,
            588 AS EMAILS_CLICKED,
            240 AS EMAILS_BOUNCED,
            12 AS EMAILS_UNSUBSCRIBED,
            CURRENT_TIMESTAMP() AS LAST_UPDATED_TIMESTAMP

        UNION ALL

        SELECT
            CURRENT_DATE() - 90 AS SEND_DATE,
            'FRANCE' AS MARKET,
            'FR' AS COUNTRY,
            'EMEA' AS REGION,
            'EX90 Announcement' AS CAMPAIGN_NAME,
            'Product Launch' AS CAMPAIGN_TYPE,
            'EX90' AS PRODUCT_LINE,
            20000 AS EMAILS_SENT,
            19600 AS EMAILS_DELIVERED,
            4900 AS EMAILS_OPENED,
            980 AS EMAILS_CLICKED,
            400 AS EMAILS_BOUNCED,
            20 AS EMAILS_UNSUBSCRIBED,
            CURRENT_TIMESTAMP() AS LAST_UPDATED_TIMESTAMP
    ) AS source_data;

-- =====================================================
-- View 2: VW_CAMPAIGN_SUMMARY
-- =====================================================
-- Campaign-level rollup for analysis

CREATE OR REPLACE VIEW VW_CAMPAIGN_SUMMARY AS
SELECT
    CAMPAIGN_NAME,
    CAMPAIGN_TYPE,
    PRODUCT_LINE,
    COUNT(DISTINCT SEND_DATE) AS TOTAL_SENDS,
    SUM(EMAILS_SENT) AS TOTAL_EMAILS_SENT,
    SUM(EMAILS_DELIVERED) AS TOTAL_EMAILS_DELIVERED,
    SUM(EMAILS_OPENED) AS TOTAL_EMAILS_OPENED,
    SUM(EMAILS_CLICKED) AS TOTAL_EMAILS_CLICKED,
    SUM(EMAILS_BOUNCED) AS TOTAL_EMAILS_BOUNCED,
    SUM(EMAILS_UNSUBSCRIBED) AS TOTAL_EMAILS_UNSUBSCRIBED,
    ROUND(AVG(OPEN_RATE), 2) AS AVG_OPEN_RATE,
    ROUND(AVG(CLICK_RATE), 2) AS AVG_CLICK_RATE,
    ROUND(AVG(BOUNCE_RATE), 2) AS AVG_BOUNCE_RATE,
    MIN(SEND_DATE) AS FIRST_SEND_DATE,
    MAX(SEND_DATE) AS LAST_SEND_DATE
FROM VW_SFMC_EMAIL_PERFORMANCE
GROUP BY CAMPAIGN_NAME, CAMPAIGN_TYPE, PRODUCT_LINE;

-- =====================================================
-- View 3: VW_MARKET_PERFORMANCE
-- =====================================================
-- Market-level performance aggregation

CREATE OR REPLACE VIEW VW_MARKET_PERFORMANCE AS
SELECT
    SEND_YEAR,
    SEND_QUARTER,
    SEND_YEAR_MONTH,
    MARKET,
    COUNTRY,
    REGION,
    COUNT(DISTINCT CAMPAIGN_NAME) AS TOTAL_CAMPAIGNS,
    SUM(EMAILS_SENT) AS TOTAL_EMAILS_SENT,
    SUM(EMAILS_DELIVERED) AS TOTAL_EMAILS_DELIVERED,
    SUM(EMAILS_OPENED) AS TOTAL_EMAILS_OPENED,
    SUM(EMAILS_CLICKED) AS TOTAL_EMAILS_CLICKED,
    ROUND(AVG(OPEN_RATE), 2) AS AVG_OPEN_RATE,
    ROUND(AVG(CLICK_RATE), 2) AS AVG_CLICK_RATE,
    ROUND(AVG(BOUNCE_RATE), 2) AS AVG_BOUNCE_RATE,
    ROUND(AVG(UNSUBSCRIBE_RATE), 2) AS AVG_UNSUBSCRIBE_RATE
FROM VW_SFMC_EMAIL_PERFORMANCE
GROUP BY SEND_YEAR, SEND_QUARTER, SEND_YEAR_MONTH, MARKET, COUNTRY, REGION;

-- =====================================================
-- Verification Queries
-- =====================================================

-- Check views were created
SHOW VIEWS LIKE 'VW_%' IN SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;

-- Test each view
SELECT 'VW_SFMC_EMAIL_PERFORMANCE' AS VIEW_NAME, COUNT(*) AS ROW_COUNT FROM VW_SFMC_EMAIL_PERFORMANCE
UNION ALL
SELECT 'VW_CAMPAIGN_SUMMARY' AS VIEW_NAME, COUNT(*) AS ROW_COUNT FROM VW_CAMPAIGN_SUMMARY
UNION ALL
SELECT 'VW_MARKET_PERFORMANCE' AS VIEW_NAME, COUNT(*) AS ROW_COUNT FROM VW_MARKET_PERFORMANCE;

-- Sample data from each view
SELECT * FROM VW_SFMC_EMAIL_PERFORMANCE LIMIT 5;
SELECT * FROM VW_CAMPAIGN_SUMMARY LIMIT 5;
SELECT * FROM VW_MARKET_PERFORMANCE LIMIT 5;

-- =====================================================
-- NEXT STEPS
-- =====================================================
-- 1. Replace the sample data with your actual SFMC tables
-- 2. Adjust column names to match your schema
-- 3. Add additional dimensions/metrics as needed
-- 4. Grant SELECT permissions to appropriate roles
-- 5. Consider materialized views for better performance

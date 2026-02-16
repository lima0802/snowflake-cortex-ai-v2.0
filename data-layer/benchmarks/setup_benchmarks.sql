-- =====================================================
-- DIA v2.0 - Benchmark Thresholds Setup
-- =====================================================
-- Purpose: Create reference table with industry benchmarks for email KPIs
-- Used for comparative analysis and performance ratings

USE DATABASE PLAYGROUND_LM;
USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;
USE WAREHOUSE TEST;

-- =====================================================
-- Table: BENCHMARK_THRESHOLDS
-- =====================================================

CREATE OR REPLACE TABLE BENCHMARK_THRESHOLDS (
    METRIC_NAME VARCHAR(50) PRIMARY KEY,
    METRIC_DESCRIPTION VARCHAR(500),
    INDUSTRY_AVG FLOAT,
    GOOD_THRESHOLD FLOAT,
    EXCELLENT_THRESHOLD FLOAT,
    POOR_THRESHOLD FLOAT,
    UNIT VARCHAR(20),
    SOURCE VARCHAR(200),
    LAST_UPDATED TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- Insert Industry Benchmarks
-- =====================================================
-- Source: Industry standards for automotive/B2C email marketing (2024)

INSERT INTO BENCHMARK_THRESHOLDS (
    METRIC_NAME,
    METRIC_DESCRIPTION,
    INDUSTRY_AVG,
    GOOD_THRESHOLD,
    EXCELLENT_THRESHOLD,
    POOR_THRESHOLD,
    UNIT,
    SOURCE
) VALUES
    (
        'OPEN_RATE',
        'Percentage of delivered emails that were opened',
        21.5,
        25.0,
        30.0,
        15.0,
        'PERCENTAGE',
        'Mailchimp Email Marketing Benchmarks 2024 - Automotive Industry'
    ),
    (
        'CLICK_RATE',
        'Percentage of delivered emails that were clicked',
        2.6,
        3.5,
        5.0,
        1.5,
        'PERCENTAGE',
        'Mailchimp Email Marketing Benchmarks 2024 - Automotive Industry'
    ),
    (
        'CLICK_TO_OPEN_RATE',
        'Percentage of opened emails that resulted in a click',
        12.0,
        15.0,
        20.0,
        8.0,
        'PERCENTAGE',
        'Campaign Monitor Email Marketing Benchmarks 2024'
    ),
    (
        'BOUNCE_RATE',
        'Percentage of sent emails that bounced',
        0.7,
        1.0,
        0.5,
        2.0,
        'PERCENTAGE',
        'Return Path Email Deliverability Report 2024'
    ),
    (
        'UNSUBSCRIBE_RATE',
        'Percentage of delivered emails that resulted in unsubscribe',
        0.1,
        0.15,
        0.05,
        0.3,
        'PERCENTAGE',
        'HubSpot Email Marketing Statistics 2024'
    ),
    (
        'DELIVERY_RATE',
        'Percentage of sent emails that were successfully delivered',
        98.0,
        99.0,
        99.5,
        95.0,
        'PERCENTAGE',
        'SendGrid Deliverability Report 2024'
    );

-- =====================================================
-- Helper View: BENCHMARK_RATINGS
-- =====================================================
-- View to help classify performance levels

CREATE OR REPLACE VIEW VW_BENCHMARK_RATINGS AS
SELECT
    METRIC_NAME,
    METRIC_DESCRIPTION,
    CASE
        WHEN UNIT = 'PERCENTAGE' THEN CONCAT(EXCELLENT_THRESHOLD, '%', ' and above')
        ELSE CONCAT('> ', EXCELLENT_THRESHOLD)
    END AS EXCELLENT_RANGE,
    CASE
        WHEN UNIT = 'PERCENTAGE' THEN CONCAT(GOOD_THRESHOLD, '%', ' - ', EXCELLENT_THRESHOLD, '%')
        ELSE CONCAT(GOOD_THRESHOLD, ' - ', EXCELLENT_THRESHOLD)
    END AS GOOD_RANGE,
    CASE
        WHEN UNIT = 'PERCENTAGE' THEN CONCAT(POOR_THRESHOLD, '%', ' - ', GOOD_THRESHOLD, '%')
        ELSE CONCAT(POOR_THRESHOLD, ' - ', GOOD_THRESHOLD)
    END AS AVERAGE_RANGE,
    CASE
        WHEN UNIT = 'PERCENTAGE' THEN CONCAT('Below ', POOR_THRESHOLD, '%')
        ELSE CONCAT('< ', POOR_THRESHOLD)
    END AS POOR_RANGE,
    SOURCE,
    LAST_UPDATED
FROM BENCHMARK_THRESHOLDS;

-- =====================================================
-- Helper Function: GET_PERFORMANCE_RATING
-- =====================================================
-- Function to rate a metric value against benchmarks

CREATE OR REPLACE FUNCTION GET_PERFORMANCE_RATING(
    METRIC_NAME_PARAM VARCHAR,
    METRIC_VALUE FLOAT
)
RETURNS VARCHAR
AS
$$
    SELECT
        CASE
            WHEN METRIC_VALUE >= EXCELLENT_THRESHOLD THEN 'Excellent'
            WHEN METRIC_VALUE >= GOOD_THRESHOLD THEN 'Good'
            WHEN METRIC_VALUE >= POOR_THRESHOLD THEN 'Average'
            ELSE 'Needs Improvement'
        END
    FROM BENCHMARK_THRESHOLDS
    WHERE METRIC_NAME = METRIC_NAME_PARAM
$$;

-- =====================================================
-- Example Usage View
-- =====================================================
-- Compare actual performance against benchmarks

CREATE OR REPLACE VIEW VW_PERFORMANCE_VS_BENCHMARK AS
SELECT
    e.CAMPAIGN_NAME,
    e.MARKET,
    e.SEND_DATE,

    -- Open Rate Comparison
    e.OPEN_RATE AS ACTUAL_OPEN_RATE,
    b_open.INDUSTRY_AVG AS BENCHMARK_OPEN_RATE,
    ROUND(e.OPEN_RATE - b_open.INDUSTRY_AVG, 2) AS OPEN_RATE_VS_BENCHMARK,
    GET_PERFORMANCE_RATING('OPEN_RATE', e.OPEN_RATE) AS OPEN_RATE_RATING,

    -- Click Rate Comparison
    e.CLICK_RATE AS ACTUAL_CLICK_RATE,
    b_click.INDUSTRY_AVG AS BENCHMARK_CLICK_RATE,
    ROUND(e.CLICK_RATE - b_click.INDUSTRY_AVG, 2) AS CLICK_RATE_VS_BENCHMARK,
    GET_PERFORMANCE_RATING('CLICK_RATE', e.CLICK_RATE) AS CLICK_RATE_RATING,

    -- Bounce Rate Comparison
    e.BOUNCE_RATE AS ACTUAL_BOUNCE_RATE,
    b_bounce.INDUSTRY_AVG AS BENCHMARK_BOUNCE_RATE,
    ROUND(e.BOUNCE_RATE - b_bounce.INDUSTRY_AVG, 2) AS BOUNCE_RATE_VS_BENCHMARK,
    GET_PERFORMANCE_RATING('BOUNCE_RATE', e.BOUNCE_RATE) AS BOUNCE_RATE_RATING

FROM VW_SFMC_EMAIL_PERFORMANCE e
CROSS JOIN (SELECT * FROM BENCHMARK_THRESHOLDS WHERE METRIC_NAME = 'OPEN_RATE') b_open
CROSS JOIN (SELECT * FROM BENCHMARK_THRESHOLDS WHERE METRIC_NAME = 'CLICK_RATE') b_click
CROSS JOIN (SELECT * FROM BENCHMARK_THRESHOLDS WHERE METRIC_NAME = 'BOUNCE_RATE') b_bounce;

-- =====================================================
-- Verification Queries
-- =====================================================

-- Check table created
SHOW TABLES LIKE 'BENCHMARK%' IN SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;

-- View benchmark data
SELECT * FROM BENCHMARK_THRESHOLDS ORDER BY METRIC_NAME;

-- View rating ranges
SELECT * FROM VW_BENCHMARK_RATINGS ORDER BY METRIC_NAME;

-- Test performance rating function
SELECT
    'OPEN_RATE' AS METRIC,
    25.0 AS VALUE,
    GET_PERFORMANCE_RATING('OPEN_RATE', 25.0) AS RATING
UNION ALL
SELECT
    'CLICK_RATE' AS METRIC,
    3.5 AS VALUE,
    GET_PERFORMANCE_RATING('CLICK_RATE', 3.5) AS RATING
UNION ALL
SELECT
    'BOUNCE_RATE' AS METRIC,
    0.5 AS VALUE,
    GET_PERFORMANCE_RATING('BOUNCE_RATE', 0.5) AS RATING;

-- Sample comparison with actual performance
SELECT * FROM VW_PERFORMANCE_VS_BENCHMARK LIMIT 5;

-- =====================================================
-- NEXT STEPS
-- =====================================================
-- 1. Review and adjust thresholds for your specific market/vertical
-- 2. Add regional benchmarks if needed (EMEA vs APAC vs Americas)
-- 3. Update benchmarks annually with latest industry data
-- 4. Consider campaign-type specific benchmarks (Newsletter vs Promotional)
-- 5. Add historical tracking of benchmark changes

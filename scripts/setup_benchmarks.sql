-- ============================================================================
-- SFMC BENCHMARK THRESHOLDS - Structured Key-Value Table
-- Purpose: Structured benchmark data for agent retrieval and Cortex Search
-- ============================================================================

USE DATABASE DEV_MARCOM_DB;
USE SCHEMA APP_DIRECTMARKETING;

-- ============================================================================
-- STEP 1: Create the structured benchmark thresholds table
-- ============================================================================
CREATE OR REPLACE TABLE CORTEX_SFMC_BENCHMARK_THRESHOLDS (
    BENCHMARK_ID VARCHAR(100) PRIMARY KEY,
    METRIC_NAME VARCHAR(50) NOT NULL,          -- open_rate, click_rate, ctor, optout_rate, bounce_rate
    EMAIL_TYPE VARCHAR(50) DEFAULT 'all',      -- all, triggered, program, campaign, enewsletter, service_reminder
    STATUS VARCHAR(20) NOT NULL,               -- critical, warning, good, strong, excellent, info
    MIN_VALUE DECIMAL(10,4),                   -- NULL means no lower bound
    MAX_VALUE DECIMAL(10,4),                   -- NULL means no upper bound
    IS_INVERSE BOOLEAN DEFAULT FALSE,
    STATUS_LABEL VARCHAR(100),
    DESCRIPTION VARCHAR(1000),
    ACTION_REQUIRED VARCHAR(500),
    INDUSTRY VARCHAR(50) DEFAULT 'premium_automotive',
    YEAR_PERIOD VARCHAR(20) DEFAULT '2024-2025',
    LAST_UPDATED TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    SEARCH_CONTENT VARCHAR(2000) 
);

-- ============================================================================
-- STEP 2: Insert Benchmarks (Open Rate, CTR, CTOR, Opt-out, Bounce)
-- ============================================================================

-- Open Rate Benchmarks
INSERT INTO CORTEX_SFMC_BENCHMARK_THRESHOLDS 
(BENCHMARK_ID, METRIC_NAME, EMAIL_TYPE, STATUS, MIN_VALUE, MAX_VALUE, IS_INVERSE, STATUS_LABEL, DESCRIPTION, ACTION_REQUIRED)
VALUES
('OR_ALL_CRITICAL', 'open_rate', 'all', 'critical', NULL, 12.0, FALSE, 'Critical - Below Benchmark', 'Open rate below 12% is significantly below premium automotive benchmark.', 'Immediate attention needed. Check deliverability, subject lines, and sender reputation.'),
('OR_ALL_WARNING', 'open_rate', 'all', 'warning', 12.0, 15.0, FALSE, 'Warning - Mass Market Average', 'Open rate 12-15% is mass-market automotive average, below premium target.', 'Monitor closely. Consider A/B testing subject lines.'),
('OR_ALL_GOOD', 'open_rate', 'all', 'good', 15.0, 25.0, FALSE, 'Good - Premium Benchmark', 'Open rate 15-25% meets premium automotive benchmark.', 'Maintain current practices.'),
('OR_ALL_STRONG', 'open_rate', 'all', 'strong', 25.0, 40.0, FALSE, 'Strong - Above Benchmark', 'Open rate 25-40% is strong performance.', 'Document best practices.'),
('OR_ALL_EXCELLENT', 'open_rate', 'all', 'excellent', 40.0, NULL, FALSE, 'Excellent - Best in Class', 'Open rate above 40% is best in class.', 'Share learnings across teams.');

-- Click Rate (CTR) Benchmarks
INSERT INTO CORTEX_SFMC_BENCHMARK_THRESHOLDS 
(BENCHMARK_ID, METRIC_NAME, EMAIL_TYPE, STATUS, MIN_VALUE, MAX_VALUE, IS_INVERSE, STATUS_LABEL, DESCRIPTION, ACTION_REQUIRED)
VALUES
('CTR_ALL_CRITICAL', 'click_rate', 'all', 'critical', NULL, 1.0, FALSE, 'Critical - Below Benchmark', 'Click rate below 1% is significantly below automotive benchmark.', 'Review content relevance and CTA clarity.'),
('CTR_ALL_WARNING', 'click_rate', 'all', 'warning', 1.0, 1.5, FALSE, 'Warning - Mass Market Average', 'Click rate 1-1.5% is mass-market automotive average.', 'Optimize CTAs and test different offers.'),
('CTR_ALL_GOOD', 'click_rate', 'all', 'good', 1.5, 3.0, FALSE, 'Good - Premium Benchmark', 'Click rate 1.5-3% meets premium automotive benchmark.', 'Maintain practices.'),
('CTR_ALL_STRONG', 'click_rate', 'all', 'strong', 3.0, 5.0, FALSE, 'Strong - Above Benchmark', 'Click rate 3-5% is strong performance.', 'Excellent engagement.'),
('CTR_ALL_EXCELLENT', 'click_rate', 'all', 'excellent', 5.0, NULL, FALSE, 'Excellent - Best in Class', 'Click rate above 5% is best in class.', 'Outstanding performance.');

-- CTOR Benchmarks
INSERT INTO CORTEX_SFMC_BENCHMARK_THRESHOLDS 
(BENCHMARK_ID, METRIC_NAME, EMAIL_TYPE, STATUS, MIN_VALUE, MAX_VALUE, IS_INVERSE, STATUS_LABEL, DESCRIPTION, ACTION_REQUIRED)
VALUES
('CTOR_ALL_CRITICAL', 'ctor', 'all', 'critical', NULL, 8.0, FALSE, 'Critical - Below Benchmark', 'CTOR below 8% is significantly below automotive benchmark.', 'Content not resonating. Review email content and CTAs.'),
('CTOR_ALL_WARNING', 'ctor', 'all', 'warning', 8.0, 12.0, FALSE, 'Warning - Mass Market Average', 'CTOR 8-12% is mass-market automotive average.', 'Improve content relevance.'),
('CTOR_ALL_GOOD', 'ctor', 'all', 'good', 12.0, 18.0, FALSE, 'Good - Premium Benchmark', 'CTOR 12-18% meets premium automotive benchmark.', 'Good content engagement.'),
('CTOR_ALL_STRONG', 'ctor', 'all', 'strong', 18.0, 25.0, FALSE, 'Strong - Above Benchmark', 'CTOR 18-25% is strong performance.', 'Excellent resonance.'),
('CTOR_ALL_EXCELLENT', 'ctor', 'all', 'excellent', 25.0, NULL, FALSE, 'Excellent - Best in Class', 'CTOR above 25% is best in class.', 'Share content strategy learnings.');

-- Opt-out Rate Benchmarks (Inverse)
INSERT INTO CORTEX_SFMC_BENCHMARK_THRESHOLDS 
(BENCHMARK_ID, METRIC_NAME, EMAIL_TYPE, STATUS, MIN_VALUE, MAX_VALUE, IS_INVERSE, STATUS_LABEL, DESCRIPTION, ACTION_REQUIRED)
VALUES
('OPTOUT_ALL_EXCELLENT', 'optout_rate', 'all', 'excellent', NULL, 0.10, TRUE, 'Excellent - Best in Class', 'Opt-out rate below 0.1% is excellent list health.', 'Outstanding stability.'),
('OPTOUT_ALL_GOOD', 'optout_rate', 'all', 'good', 0.15, 0.25, TRUE, 'Good - Premium Standard', 'Opt-out rate 0.15-0.25% is premium standard.', 'Normal levels.'),
('OPTOUT_ALL_CRITICAL', 'optout_rate', 'all', 'critical', 0.40, NULL, TRUE, 'Critical - Immediate Action', 'Opt-out rate above 0.4% indicates email fatigue.', 'Immediate attention needed.');

-- Bounce Rate Benchmarks (Inverse)
INSERT INTO CORTEX_SFMC_BENCHMARK_THRESHOLDS 
(BENCHMARK_ID, METRIC_NAME, EMAIL_TYPE, STATUS, MIN_VALUE, MAX_VALUE, IS_INVERSE, STATUS_LABEL, DESCRIPTION, ACTION_REQUIRED)
VALUES
('BOUNCE_ALL_EXCELLENT', 'bounce_rate', 'all', 'excellent', NULL, 0.30, TRUE, 'Excellent - Best in Class', 'Bounce rate below 0.3% is excellent higiene.', 'Maintain list cleanup.'),
('BOUNCE_ALL_GOOD', 'bounce_rate', 'all', 'good', 0.50, 1.50, TRUE, 'Good - Automotive Benchmark', 'Bounce rate 0.5-1.5% is standard benchmark.', 'Acceptable levels.'),
('BOUNCE_ALL_CRITICAL', 'bounce_rate', 'all', 'critical', 2.50, NULL, TRUE, 'Critical - Immediate Action', 'Bounce rate above 2.5% damages reputation.', 'Immediate list cleanup required.');

-- Context Records
INSERT INTO CORTEX_SFMC_BENCHMARK_THRESHOLDS 
(BENCHMARK_ID, METRIC_NAME, EMAIL_TYPE, STATUS, MIN_VALUE, MAX_VALUE, IS_INVERSE, STATUS_LABEL, DESCRIPTION, ACTION_REQUIRED)
VALUES
('CONTEXT_APPLE_MPP', 'open_rate', 'all', 'info', NULL, NULL, FALSE, 'Important Context', 'Open rates may be inflated due to Apple Mail Privacy Protection (MPP).', 'Use CTOR as primary metric.'),
('CONTEXT_CTOR_PRIMARY', 'ctor', 'all', 'info', NULL, NULL, FALSE, 'Primary Metric', 'CTOR is the PRIMARY engagement metric for 2024-2025 due to Apple MPP.', 'Prioritize CTOR over open rate.');

-- ============================================================================
-- STEP 3: Update SEARCH_CONTENT column for Cortex Search
-- ============================================================================
UPDATE CORTEX_SFMC_BENCHMARK_THRESHOLDS
SET SEARCH_CONTENT = CONCAT(
    'Metric: ', METRIC_NAME, '. ',
    'Type: ', EMAIL_TYPE, '. ',
    'Status: ', STATUS, ' (', COALESCE(STATUS_LABEL, ''), '). ',
    'Range: ', 
    CASE 
        WHEN MIN_VALUE IS NULL THEN 'Below ' || MAX_VALUE || '%'
        WHEN MAX_VALUE IS NULL THEN 'Above ' || MIN_VALUE || '%'
        ELSE MIN_VALUE || '% to ' || MAX_VALUE || '%'
    END, '. ',
    'Info: ', COALESCE(DESCRIPTION, ''), ' ',
    'Action: ', COALESCE(ACTION_REQUIRED, '')
);

-- ============================================================================
-- STEP 4: Create Cortex Search Service
-- ============================================================================
CREATE OR REPLACE CORTEX SEARCH SERVICE CORTEX_SFMC_BENCHMARK_SEARCH
ON SEARCH_CONTENT
ATTRIBUTES METRIC_NAME, EMAIL_TYPE, STATUS, INDUSTRY, YEAR_PERIOD
WAREHOUSE = DEV_MARCOM_APP_DIRECTMARKETING_ETL_WHS
TARGET_LAG = '1 hour'
AS (
    SELECT * FROM CORTEX_SFMC_BENCHMARK_THRESHOLDS
);

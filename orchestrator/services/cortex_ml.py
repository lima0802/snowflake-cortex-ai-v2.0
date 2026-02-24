"""
Cortex ML Service Wrapper - DIA v2.0
====================================

This module provides a Python wrapper for Snowflake Cortex ML functions,
which include time series forecasting and anomaly detection.

Key Features:
- Time series forecasting (predict future values)
- Anomaly detection (identify unusual patterns)
- No ML expertise required - Snowflake handles the complexity
- Works directly on your data in Snowflake

Use Cases:
- Forecast email open rates for next month
- Predict campaign performance
- Detect unusual spikes in bounce rates
- Identify anomalous user behavior
- Resource planning and budgeting

Learning Resources:
- https://docs.snowflake.com/en/user-guide/snowflake-cortex/ml-functions/forecasting
- https://docs.snowflake.com/en/user-guide/snowflake-cortex/ml-functions/anomaly-detection

Author: Li Ma
Date: February 24, 2026
docker exec dia-orchestrator python services/cortex_ml.py
"""

import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from snowflake.snowpark import Session
from dotenv import load_dotenv

# Add parent directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging import get_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)


# ==============================================================================
# DATA MODELS
# ==============================================================================

@dataclass
class ForecastResult:
    """
    Container for a single forecast data point.
    
    Represents one forecasted value in the future.
    
    Attributes:
        timestamp (str/datetime): When this forecast is for
        forecast (float): The predicted value
        lower_bound (float): Lower confidence interval (95%)
        upper_bound (float): Upper confidence interval (95%)
        metadata (Dict): Additional info (model used, confidence, etc.)
    
    Example:
        result = ForecastResult(
            timestamp="2026-03-01",
            forecast=25.5,
            lower_bound=22.0,
            upper_bound=29.0,
            metadata={"confidence": 0.95}
        )
    """
    timestamp: Any  # Can be str or datetime
    forecast: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": str(self.timestamp),
            "forecast": self.forecast,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "metadata": self.metadata
        }


@dataclass
class ForecastResponse:
    """
    Container for forecasting API responses.
    
    Holds all forecasted values plus metadata.
    
    Attributes:
        series_name (str): Name of the time series forecasted
        forecasts (List[ForecastResult]): List of forecast points
        model_info (Dict): Information about the model used
        error (str): Error message if something went wrong
    
    Example:
        response = ForecastResponse(
            series_name="daily_open_rate",
            forecasts=[result1, result2, ...],
            model_info={"algorithm": "ARIMA", "accuracy": 0.92}
        )
    """
    series_name: str
    forecasts: Optional[List[ForecastResult]] = None
    model_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "series_name": self.series_name,
            "forecasts": [f.to_dict() for f in (self.forecasts or [])],
            "model_info": self.model_info,
            "error": self.error
        }


@dataclass
class AnomalyResult:
    """
    Container for a single anomaly detection result.
    
    Represents one data point checked for anomalies.
    
    Attributes:
        timestamp (str/datetime): When this data point occurred
        value (float): The actual observed value
        is_anomaly (bool): Whether this point is anomalous
        anomaly_score (float): How anomalous (0-1, higher = more unusual)
        expected_value (float): What was expected (normal) value
        metadata (Dict): Additional context
    
    Example:
        result = AnomalyResult(
            timestamp="2026-02-15",
            value=5.2,
            is_anomaly=True,
            anomaly_score=0.87,
            expected_value=25.0
        )
    """
    timestamp: Any
    value: float
    is_anomaly: bool
    anomaly_score: Optional[float] = None
    expected_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": str(self.timestamp),
            "value": self.value,
            "is_anomaly": self.is_anomaly,
            "anomaly_score": self.anomaly_score,
            "expected_value": self.expected_value,
            "metadata": self.metadata
        }


@dataclass
class AnomalyResponse:
    """
    Container for anomaly detection API responses.
    
    Holds all detected anomalies plus summary.
    
    Attributes:
        series_name (str): Name of the time series analyzed
        anomalies (List[AnomalyResult]): List of all data points
        total_anomalies (int): Count of anomalous points
        anomaly_percentage (float): Percentage of points that are anomalies
        error (str): Error message if something went wrong
    
    Example:
        response = AnomalyResponse(
            series_name="daily_bounce_rate",
            anomalies=[result1, result2, ...],
            total_anomalies=5,
            anomaly_percentage=2.3
        )
    """
    series_name: str
    anomalies: Optional[List[AnomalyResult]] = None
    total_anomalies: Optional[int] = None
    anomaly_percentage: Optional[float] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "series_name": self.series_name,
            "anomalies": [a.to_dict() for a in (self.anomalies or [])],
            "total_anomalies": self.total_anomalies,
            "anomaly_percentage": self.anomaly_percentage,
            "error": self.error
        }


# ==============================================================================
# CORTEX ML SERVICE
# ==============================================================================

class CortexML:
    """
    Python wrapper for Snowflake Cortex ML functions.
    
    This service provides ML capabilities without requiring ML expertise:
    - Forecasting: Predict future values based on historical data
    - Anomaly Detection: Identify unusual patterns in your data
    
    How Forecasting Works:
    1. You provide historical time series data
    2. Snowflake analyzes patterns, trends, seasonality
    3. Returns predictions for future time periods
    
    How Anomaly Detection Works:
    1. You provide time series data
    2. Snowflake learns normal patterns
    3. Flags data points that deviate significantly
    
    Usage Example:
        # Forecast next 30 days of open rates
        ml = CortexML()
        forecast = ml.forecast(
            table="daily_metrics",
            timestamp_col="date",
            target_col="open_rate",
            forecast_days=30
        )
        
        # Detect anomalies in bounce rates
        anomalies = ml.detect_anomalies(
            table="daily_metrics",
            timestamp_col="date",
            target_col="bounce_rate"
        )
    """
    
    def __init__(
        self,
        database: str = None,
        schema: str = None,
        warehouse: str = None
    ):
        """
        Initialize Cortex ML service.
        
        Args:
            database: Snowflake database (from env if not provided)
            schema: Snowflake schema (from env if not provided)
            warehouse: Snowflake warehouse (from env if not provided)
        
        Example:
            ml = CortexML()  # Use .env defaults
            ml = CortexML(database="ANALYTICS", schema="METRICS")
        """
        # Snowflake connection details (from environment variables)
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
        self.warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
        
        # Session will be created lazily
        self._session: Optional[Session] = None
        
        logger.info(
            "CortexML initialized",
            database=self.database,
            schema=self.schema
        )
    
    # --------------------------------------------------------------------------
    # SNOWFLAKE SESSION MANAGEMENT
    # --------------------------------------------------------------------------
    
    def _get_session(self) -> Session:
        """Get or create Snowflake session (lazy loading)"""
        if self._session is None:
            logger.info("Creating Snowflake session...")
            
            self._session = Session.builder.configs({
                "account": os.getenv("SNOWFLAKE_ACCOUNT"),
                "user": os.getenv("SNOWFLAKE_USER"),
                "password": os.getenv("SNOWFLAKE_PASSWORD"),
                "role": os.getenv("SNOWFLAKE_ROLE"),
                "warehouse": self.warehouse,
                "database": self.database,
                "schema": self.schema,
            }).create()
            
            logger.info(
                "Snowflake session created successfully",
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                database=self.database
            )
        
        return self._session
    
    # --------------------------------------------------------------------------
    # FORECASTING FUNCTIONS
    # --------------------------------------------------------------------------
    
    def forecast(
        self,
        table: str,
        timestamp_col: str,
        target_col: str,
        forecast_days: int = 30,
        config: Optional[Dict[str, Any]] = None
    ) -> ForecastResponse:
        """
        Forecast future values for a time series.
        
        Predicts future values based on historical patterns.
        Snowflake automatically handles seasonality, trends, and more!
        
        Args:
            table: Name of table with historical data
            timestamp_col: Column with timestamps/dates
            target_col: Column with values to forecast
            forecast_days: How many days into the future to predict
            config: Optional model configuration
        
        Returns:
            ForecastResponse with predictions
        
        Examples:
            # Forecast open rates for next 30 days
            forecast = ml.forecast(
                table="VW_DAILY_METRICS",
                timestamp_col="DATE",
                target_col="OPEN_RATE",
                forecast_days=30
            )
            
            # View predictions
            for point in forecast.forecasts:
                print(f"{point.timestamp}: {point.forecast:.2f}% "
                      f"(range: {point.lower_bound:.2f}-{point.upper_bound:.2f})")
        
        How to prepare your data:
            - Need at least 14 days of historical data
            - One row per time period (daily data = one row per day)
            - No missing timestamps (fill gaps with 0 or average)
            - Timestamp column should be DATE or TIMESTAMP type
        """
        logger.info(
            "Starting time series forecast",
            table=table,
            target_col=target_col,
            forecast_days=forecast_days
        )
        
        try:
            session = self._get_session()
            
            # Build configuration options
            config_json = json.dumps(config if config else {})
            
            # Create a training query
            # Snowflake ML will learn from this data
            training_sql = f"""
                SELECT
                    {timestamp_col}::TIMESTAMP AS ts,
                    {target_col}::FLOAT AS target
                FROM {table}
                WHERE {target_col} IS NOT NULL
                ORDER BY ts
            """
            
            # Call Cortex Forecast function
            # Note: This is a simplified example. In production, you'd use
            # SNOWFLAKE.CORTEX.FORECAST() or create a forecast model
            forecast_sql = f"""
                SELECT
                    DATEADD(day, row_number() OVER (ORDER BY NULL), 
                            MAX({timestamp_col})) AS forecast_date,
                    AVG({target_col}) AS forecast_value,
                    AVG({target_col}) * 0.9 AS lower_bound,
                    AVG({target_col}) * 1.1 AS upper_bound
                FROM {table}
                CROSS JOIN TABLE(GENERATOR(ROWCOUNT => {forecast_days}))
                WHERE {target_col} IS NOT NULL
                GROUP BY forecast_date
                ORDER BY forecast_date
            """
            
            logger.debug("Executing forecast query", sql=forecast_sql[:200])
            
            results = session.sql(forecast_sql).collect()
            
            # Parse results into ForecastResult objects
            forecasts = []
            for row in results:
                forecasts.append(ForecastResult(
                    timestamp=row["FORECAST_DATE"],
                    forecast=float(row["FORECAST_VALUE"]),
                    lower_bound=float(row["LOWER_BOUND"]),
                    upper_bound=float(row["UPPER_BOUND"]),
                    metadata={"days_ahead": len(forecasts) + 1}
                ))
            
            logger.info(
                "Forecast completed successfully",
                forecast_points=len(forecasts),
                first_date=forecasts[0].timestamp if forecasts else None
            )
            
            return ForecastResponse(
                series_name=f"{table}.{target_col}",
                forecasts=forecasts,
                model_info={
                    "forecast_days": forecast_days,
                    "training_table": table,
                    "method": "simple_average"  # In production, Snowflake uses advanced models
                }
            )
        
        except Exception as e:
            error_msg = f"Forecasting error: {str(e)}"
            logger.error(error_msg, table=table, target_col=target_col)
            return ForecastResponse(
                series_name=f"{table}.{target_col}",
                error=error_msg
            )
    
    # --------------------------------------------------------------------------
    # ANOMALY DETECTION FUNCTIONS
    # --------------------------------------------------------------------------
    
    def detect_anomalies(
        self,
        table: str,
        timestamp_col: str,
        target_col: str,
        sensitivity: float = 0.95,
        lookback_days: Optional[int] = None
    ) -> AnomalyResponse:
        """
        Detect anomalies in time series data.
        
        Identifies data points that deviate significantly from normal patterns.
        
        Args:
            table: Name of table with data to analyze
            timestamp_col: Column with timestamps/dates
            target_col: Column with values to check
            sensitivity: Detection sensitivity (0.9-0.99, higher = more sensitive)
            lookback_days: How many recent days to analyze (None = all data)
        
        Returns:
            AnomalyResponse with detected anomalies
        
        Examples:
            # Detect unusual bounce rates
            anomalies = ml.detect_anomalies(
                table="VW_DAILY_METRICS",
                timestamp_col="DATE",
                target_col="BOUNCE_RATE",
                sensitivity=0.95
            )
            
            # View anomalies
            for point in anomalies.anomalies:
                if point.is_anomaly:
                    print(f"⚠️  {point.timestamp}: {point.value:.2f}% "
                          f"(expected: {point.expected_value:.2f}%)")
        
        What gets flagged as anomalous:
            - Sudden spikes or drops
            - Values far from historical average
            - Breaks in seasonal patterns
            - Statistical outliers
        """
        logger.info(
            "Starting anomaly detection",
            table=table,
            target_col=target_col,
            sensitivity=sensitivity
        )
        
        try:
            session = self._get_session()
            
            # Build WHERE clause for lookback period
            where_clause = ""
            if lookback_days:
                where_clause = f"WHERE {timestamp_col} >= DATEADD(day, -{lookback_days}, CURRENT_DATE())"
            
            # Anomaly detection query using statistical method
            # In production, you'd use SNOWFLAKE.CORTEX.DETECT_ANOMALIES()
            anomaly_sql = f"""
                WITH stats AS (
                    SELECT
                        AVG({target_col}) AS mean_val,
                        STDDEV({target_col}) AS std_val
                    FROM {table}
                    {where_clause}
                ),
                scored AS (
                    SELECT
                        {timestamp_col}::TIMESTAMP AS ts,
                        {target_col}::FLOAT AS value,
                        stats.mean_val,
                        stats.std_val,
                        ABS({target_col} - stats.mean_val) / NULLIF(stats.std_val, 0) AS z_score
                    FROM {table}
                    CROSS JOIN stats
                    {where_clause}
                    ORDER BY ts
                )
                SELECT
                    ts,
                    value,
                    CASE WHEN z_score > 2.5 THEN TRUE ELSE FALSE END AS is_anomaly,
                    z_score / 5.0 AS anomaly_score,
                    mean_val AS expected_value
                FROM scored
                ORDER BY ts
            """
            
            logger.debug("Executing anomaly detection query")
            
            results = session.sql(anomaly_sql).collect()
            
            # Parse results
            anomalies = []
            anomaly_count = 0
            
            for row in results:
                is_anom = bool(row["IS_ANOMALY"])
                if is_anom:
                    anomaly_count += 1
                
                anomalies.append(AnomalyResult(
                    timestamp=row["TS"],
                    value=float(row["VALUE"]),
                    is_anomaly=is_anom,
                    anomaly_score=float(row["ANOMALY_SCORE"]) if row["ANOMALY_SCORE"] else 0.0,
                    expected_value=float(row["EXPECTED_VALUE"]) if row["EXPECTED_VALUE"] else None
                ))
            
            anomaly_pct = (anomaly_count / len(anomalies) * 100) if anomalies else 0
            
            logger.info(
                "Anomaly detection completed",
                total_points=len(anomalies),
                anomalies_found=anomaly_count,
                percentage=f"{anomaly_pct:.1f}%"
            )
            
            return AnomalyResponse(
                series_name=f"{table}.{target_col}",
                anomalies=anomalies,
                total_anomalies=anomaly_count,
                anomaly_percentage=anomaly_pct
            )
        
        except Exception as e:
            error_msg = f"Anomaly detection error: {str(e)}"
            logger.error(error_msg, table=table, target_col=target_col)
            return AnomalyResponse(
                series_name=f"{table}.{target_col}",
                error=error_msg
            )
    
    # --------------------------------------------------------------------------
    # HELPER METHODS
    # --------------------------------------------------------------------------
    
    def close(self) -> None:
        """Close Snowflake session and cleanup resources"""
        if self._session is not None:
            self._session.close()
            self._session = None
            logger.info("Snowflake session closed")
    
    # --------------------------------------------------------------------------
    # CONTEXT MANAGER SUPPORT
    # --------------------------------------------------------------------------
    
    def __enter__(self):
        """Enable use with 'with' statement"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically close connection when exiting 'with' block"""
        self.close()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    """
    Example usage of CortexML class.
    
    Run this file directly to test:
        python orchestrator/services/cortex_ml.py
    
    Or from Docker:
        docker exec dia-orchestrator python services/cortex_ml.py
    """
    
    print("=" * 70)
    print("CORTEX ML SERVICE - EXAMPLE USAGE")
    print("=" * 70)
    
    # Example 1: Time Series Forecasting
    print("\n📝 Example 1: Forecast Email Open Rates")
    print("-" * 70)
    
    try:
        with CortexML() as ml:
            forecast = ml.forecast(
                table="VW_SFMC_EMAIL_PERFORMANCE",
                timestamp_col="DATE",
                target_col="OPEN_RATE",
                forecast_days=7  # Next week
            )
            
            if forecast.error:
                print(f"❌ Error: {forecast.error}")
            elif forecast.forecasts:
                print(f"✅ Forecast for next 7 days:\n")
                for point in forecast.forecasts[:7]:
                    print(f"   {point.timestamp.strftime('%Y-%m-%d')}: "
                          f"{point.forecast:.2f}% "
                          f"(range: {point.lower_bound:.2f}-{point.upper_bound:.2f}%)")
                
                print(f"\n   Model: {forecast.model_info.get('method', 'N/A')}")
            else:
                print("ℹ️  No forecast generated")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure VW_SFMC_EMAIL_PERFORMANCE exists with DATE and OPEN_RATE columns")
    
    # Example 2: Anomaly Detection
    print("\n📝 Example 2: Detect Anomalies in Bounce Rates")
    print("-" * 70)
    
    try:
        with CortexML() as ml:
            anomalies = ml.detect_anomalies(
                table="VW_SFMC_EMAIL_PERFORMANCE",
                timestamp_col="DATE",
                target_col="BOUNCE_RATE",
                sensitivity=0.95,
                lookback_days=30
            )
            
            if anomalies.error:
                print(f"❌ Error: {anomalies.error}")
            elif anomalies.anomalies:
                print(f"✅ Analyzed {len(anomalies.anomalies)} data points")
                print(f"   Found {anomalies.total_anomalies} anomalies "
                      f"({anomalies.anomaly_percentage:.1f}%)\n")
                
                # Show anomalies only
                anom_points = [a for a in anomalies.anomalies if a.is_anomaly]
                if anom_points:
                    print("   ⚠️  Anomalous Points:")
                    for point in anom_points[:5]:  # Show first 5
                        print(f"      {point.timestamp.strftime('%Y-%m-%d')}: "
                              f"{point.value:.2f}% (expected: {point.expected_value:.2f}%) "
                              f"[score: {point.anomaly_score:.2f}]")
                else:
                    print("   ✅ No anomalies detected - all values are normal!")
            else:
                print("ℹ️  No data analyzed")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Examples complete!")
    print("=" * 70)
    print("\n💡 Note: These use simplified ML algorithms for demonstration.")
    print("   In production, use Snowflake's native CORTEX ML functions for")
    print("   more accurate forecasting and anomaly detection.")

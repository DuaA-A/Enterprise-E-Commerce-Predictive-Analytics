# AI Model Documentation & Metrics Report

## Overview
This section outlines the advanced Machine Learning models integrated into the Medallion Data Pipeline. By combining time-series forecasting with classification algorithms, we transformed the `Gold Layer` structured historical data into predictive analytics outputs designed specifically for Power BI dashboards.

---

## 1. Time-Series Demand Forecasting
**Algorithm Used**: Facebook Prophet
**Purpose**: Forecast daily sales volume (Units) and gross income (Revenue) 60 days into the future.
**Input Features**: Historical `Revenue`, `Units`, and temporal features derived from `dim_date.csv`.

### KPIs & Metrics
*   **MAPE (Mean Absolute Percentage Error)**: Target < 10%
*   **Seasonality Detected**: Weekly (weekend surges) and Yearly (Q4 holiday spikes).
*   **Dashboard Visual**: *Revenue Forecast Line Chart* with an 80% confidence interval band showing Best/Worst case revenue scenarios.

### Generated Output
*   `predicted_revenue_dashboard.csv`: Contains `Date`, `Predicted_Revenue`, `Pessimistic_Revenue`, and `Optimistic_Revenue`.

---

## 2. Bleeding SKU Detection (Margin Prediction)
**Algorithm Used**: Random Forest Classifier
**Purpose**: Actively detect which specific products (SKUs) are at high risk of dropping below a 10% Net Profit Margin in the upcoming days.
**Input Features**: `PPC Cost`, `FBA Fees`, `Promo Amount`, `Sessions`, `Clicks`, `Page Views`, and 7-Day Rolling Revenue.

### KPIs & Metrics
*   **Precision/Recall**: Ensures we don't falsely flag profitable items while catching genuine profit bleeders.
*   **Top Feature Drivers (Feature Importance)**: 
    1. `PPC Cost`
    2. `FBA Fees`
    3. `Unit Session %` (Conversion Rate)

### Generated Insights
*   **PPC Inefficiency**: High PPC costs without proportional session conversions are the primary driver of "Bleeding SKUs".
*   **Dashboard Visual**: *Bleeding Risk Matrix* highlighting SKUs in the "Danger Zone".

### Generated Output
*   `sku_risk_dashboard.csv`: Contains `Product_Key`, `Title`, and the `Predicted_Bleeding_Risk` probability (0.0 to 1.0).

---

## How to Execute the AI Pipeline
1.  **Prerequisites**: Ensure you have Python installed with `pandas`, `prophet`, `scikit-learn`, and `matplotlib`.
2.  **Data Prep**: Run all cells in `01_data_preparation.ipynb` to merge the Gold Layer data into `ml_ready_data.csv`.
3.  **Forecasting**: Run `02_demand_forecasting_prophet.ipynb` to train the Prophet model and generate `predicted_revenue_dashboard.csv`.
4.  **Risk Detection**: Run `03_profitability_prediction_rf.ipynb` to train the Random Forest and generate `sku_risk_dashboard.csv`.
5.  **Dashboard Integration**: Import the two generated `.csv` files into your Power BI `.pbix` file. Link the `Date` and `Product_Key` columns to your existing Star Schema relationships.

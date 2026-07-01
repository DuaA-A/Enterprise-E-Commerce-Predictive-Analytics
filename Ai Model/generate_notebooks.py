import nbformat as nbf
import os

# Define notebooks and their cells
notebooks = {
    "01_data_preparation.ipynb": [
        {"type": "markdown", "content": "# Data Preparation for Predictive Analytics\nThis notebook merges the Medallion Architecture Gold Layer data (`fact_sales.csv`, `dim_date.csv`, `dim_product.csv`) into a flattened ML-ready dataset."},
        {"type": "code", "content": "import pandas as pd\nimport numpy as np\nimport os\nimport warnings\nwarnings.filterwarnings('ignore')\n\n# Define paths\nbase_path = '../Medallion Architecture/Gold Layer/'\nfact_sales_path = os.path.join(base_path, 'fact_sales.csv')\ndim_date_path = os.path.join(base_path, 'dim_date.csv')\ndim_product_path = os.path.join(base_path, 'dim_product.csv')"},
        {"type": "markdown", "content": "## Load Gold Layer Data"},
        {"type": "code", "content": "df_sales = pd.read_csv(fact_sales_path)\ndf_date = pd.read_csv(dim_date_path)\ndf_product = pd.read_csv(dim_product_path)\n\nprint(f\"Sales shape: {df_sales.shape}\")\nprint(f\"Date shape: {df_date.shape}\")\nprint(f\"Product shape: {df_product.shape}\")"},
        {"type": "markdown", "content": "## Merge Dimensions into Facts"},
        {"type": "code", "content": "df_merged = df_sales.merge(df_date[['Date_Key', 'Date', 'Day', 'Month', 'Year', 'Is_Weekend']], on='Date_Key', how='left')\ndf_merged = df_merged.merge(df_product[['Product_Key', 'Parent ASIN', 'Title', 'Brand']], on='Product_Key', how='left')\n\n# Convert Date to datetime\ndf_merged['Date'] = pd.to_datetime(df_merged['Date'])\ndf_merged = df_merged.sort_values('Date')\ndisplay(df_merged.head())"},
        {"type": "markdown", "content": "## Feature Engineering\nCreating lag features and rolling averages for ML."},
        {"type": "code", "content": "# Calculate rolling 7-day averages for key metrics per product\ndf_merged['Revenue_7d_avg'] = df_merged.groupby('Product_Key')['Revenue'].transform(lambda x: x.rolling(7, min_periods=1).mean())\ndf_merged['Units_7d_avg'] = df_merged.groupby('Product_Key')['Units'].transform(lambda x: x.rolling(7, min_periods=1).mean())\n\n# Flag Bleeding SKUs (Net Margin < 0.1)\ndf_merged['Is_Bleeding'] = (df_merged['Net Margin'] < 0.10).astype(int)\n\ndf_merged.to_csv('ml_ready_data.csv', index=False)\nprint(\"Saved ML-ready data to 'ml_ready_data.csv'\")"}
    ],
    "02_demand_forecasting_prophet.ipynb": [
        {"type": "markdown", "content": "# Time-Series Demand & Revenue Forecasting (Prophet)\nThis model forecasts `Units` and `Revenue` 30-90 days into the future for the AI Dashboard."},
        {"type": "code", "content": "import pandas as pd\nimport numpy as np\nfrom prophet import Prophet\nfrom sklearn.metrics import mean_absolute_percentage_error, mean_squared_error\nimport matplotlib.pyplot as plt\nimport os\nimport warnings\nwarnings.filterwarnings('ignore')\n\n# Load prepared data\ndf = pd.read_csv('ml_ready_data.csv')\ndf['Date'] = pd.to_datetime(df['Date'])"},
        {"type": "markdown", "content": "## Aggregate Daily Global Demand"},
        {"type": "code", "content": "daily_demand = df.groupby('Date').agg({'Units': 'sum', 'Revenue': 'sum'}).reset_index()\n\n# Prepare for Prophet (Revenue)\ndf_prophet = daily_demand[['Date', 'Revenue']].rename(columns={'Date': 'ds', 'Revenue': 'y'})\n\n# Train-Test Split (Last 30 days as test)\ntrain = df_prophet[:-30]\ntest = df_prophet[-30:]"},
        {"type": "markdown", "content": "## Train Prophet Model (Revenue)"},
        {"type": "code", "content": "model = Prophet(yearly_seasonality=True, weekly_seasonality=True)\nmodel.fit(train)\n\nfuture = model.make_future_dataframe(periods=60) # Predict 30 days of test + 30 days future\nforecast = model.predict(future)"},
        {"type": "markdown", "content": "## Evaluate & Visualize"},
        {"type": "code", "content": "forecast_test = forecast[['ds', 'yhat']].tail(60).head(30)\nmape = mean_absolute_percentage_error(test['y'], forecast_test['yhat'])\nprint(f\"Revenue Forecast MAPE: {mape:.2%}\")\n\nfig1 = model.plot(forecast)\nplt.title(\"Revenue Forecast\")\nplt.show()"},
        {"type": "markdown", "content": "## Export Dashboard Data"},
        {"type": "code", "content": "# Predict future 60 days from max date\nmodel_full = Prophet(yearly_seasonality=True, weekly_seasonality=True)\nmodel_full.fit(df_prophet)\nfuture_full = model_full.make_future_dataframe(periods=60)\nforecast_full = model_full.predict(future_full)\n\n# Save to CSV for Power BI\nforecast_output = forecast_full[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(60)\nforecast_output = forecast_output.rename(columns={'ds': 'Date', 'yhat': 'Predicted_Revenue', 'yhat_lower': 'Pessimistic_Revenue', 'yhat_upper': 'Optimistic_Revenue'})\nforecast_output.to_csv('predicted_revenue_dashboard.csv', index=False)\nprint(\"Exported 'predicted_revenue_dashboard.csv'\")"}
    ],
    "03_profitability_prediction_rf.ipynb": [
        {"type": "markdown", "content": "# Bleeding SKU & Net Margin Prediction (Random Forest)\nThis model classifies whether a product will bleed profit margin and identifies feature importance (e.g., PPC vs FBA impacts)."},
        {"type": "code", "content": "import pandas as pd\nimport numpy as np\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.ensemble import RandomForestRegressor, RandomForestClassifier\nfrom sklearn.metrics import classification_report, mean_squared_error\nimport matplotlib.pyplot as plt\n\n# Load prepared data\ndf = pd.read_csv('ml_ready_data.csv')"},
        {"type": "markdown", "content": "## Prepare Features (X) and Target (y)"},
        {"type": "code", "content": "# Predict next day's profitability based on today's metrics\ndf = df.sort_values(['Product_Key', 'Date'])\ndf['Next_Day_Margin'] = df.groupby('Product_Key')['Net Margin'].shift(-1)\ndf['Next_Day_Bleeding'] = (df['Next_Day_Margin'] < 0.10).astype(int)\n\ndf_clean = df.dropna(subset=['Next_Day_Margin'])\n\nfeatures = ['Sessions', 'Page Views', 'Clicks', 'PPC Cost', 'FBA Fees', 'Promo Amount', 'Unit Session %', 'Revenue_7d_avg']\nX = df_clean[features].fillna(0)\ny_reg = df_clean['Next_Day_Margin']\ny_clf = df_clean['Next_Day_Bleeding']\n\nX_train, X_test, y_train, y_test = train_test_split(X, y_clf, test_size=0.2, random_state=42)"},
        {"type": "markdown", "content": "## Train Random Forest Classifier"},
        {"type": "code", "content": "clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)\nclf.fit(X_train, y_train)\n\ny_pred = clf.predict(X_test)\nprint(\"Bleeding SKU Detection Report:\")\nprint(classification_report(y_test, y_pred))"},
        {"type": "markdown", "content": "## Feature Importance"},
        {"type": "code", "content": "importances = clf.feature_importances_\nindices = np.argsort(importances)[::-1]\n\nplt.figure(figsize=(10, 6))\nplt.title(\"Drivers of Margin Bleeding\")\nplt.bar(range(X.shape[1]), importances[indices], align=\"center\")\nplt.xticks(range(X.shape[1]), [features[i] for i in indices], rotation=45)\nplt.tight_layout()\nplt.show()"},
        {"type": "markdown", "content": "## Export Predictions for Dashboard"},
        {"type": "code", "content": "# Predict on latest available date\nlatest_data = df.groupby('Product_Key').last().reset_index()\nX_latest = latest_data[features].fillna(0)\nlatest_data['Predicted_Bleeding_Risk'] = clf.predict_proba(X_latest)[:, 1]\n\nrisk_dashboard = latest_data[['Product_Key', 'Title', 'Predicted_Bleeding_Risk']]\nrisk_dashboard.to_csv('sku_risk_dashboard.csv', index=False)\nprint(\"Exported 'sku_risk_dashboard.csv'\")"}
    ]
}

# Generate notebooks
for nb_name, cells in notebooks.items():
    nb = nbf.v4.new_notebook()
    nb_cells = []
    for cell in cells:
        if cell["type"] == "markdown":
            nb_cells.append(nbf.v4.new_markdown_cell(cell["content"]))
        elif cell["type"] == "code":
            nb_cells.append(nbf.v4.new_code_cell(cell["content"]))
    nb['cells'] = nb_cells
    
    with open(nb_name, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
        
print(\"Notebooks generated successfully.\")

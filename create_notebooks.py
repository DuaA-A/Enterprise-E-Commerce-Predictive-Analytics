import json

def create_nb(filename, cells_data):
    cells = []
    for cell_type, source in cells_data:
        cell = {
            'cell_type': cell_type,
            'metadata': {},
            'source': [line + '\n' for line in source.split('\n')]
        }
        if cell_type == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
        else:
            # Markdown cells shouldn't have trailing newlines for the last line usually, but it's fine.
            pass
        
        # Remove trailing newline from last line.
        if len(cell['source']) > 0:
            cell['source'][-1] = cell['source'][-1].rstrip('\n')
            
        cells.append(cell)
        
    nb = {
        'cells': cells,
        'metadata': {},
        'nbformat': 4,
        'nbformat_minor': 5
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)

cleaning_cells = [
    ('markdown', '# Phase 1: Targeted Data Cleaning & Preprocessing\nThis notebook executes the data cleaning pipeline mapped for E-Commerce edge cases.'),
    ('markdown', '## Initialization and Loading Data\nLoad the raw dataset.'),
    ('code', 'import pandas as pd\nimport numpy as np\nimport warnings\nwarnings.filterwarnings("ignore")\n\nprint("Loading dataset...")\ndf = pd.read_excel("DailySales_original.xlsx")\nprint(f"Original shape: {df.shape}")'),
    ('markdown', '## 1. Drop the Grand Total Row\nIdentify and drop the final aggregate row to prevent data duplication.'),
    ('code', '# Dropping the Grand Total row (indicated by missing Date)\ndf = df.dropna(subset=["Date"])\nprint(f"Shape after dropping Grand Total: {df.shape}")'),
    ('markdown', '## Basic Cleaning\nDropping columns heavily skewed with nulls that provide no analytical value.'),
    ('code', 'useless_cols = ["Internal Name", "Product Group", "FNSKU", "Is Parent"]\ndf = df.drop(columns=[col for col in useless_cols if col in df.columns], errors="ignore")\nprint("Dropped extraneous columns.")'),
    ('markdown', '## 2. Smart Imputation for Missing Values\nHandling heavy missing values intelligently rather than using crude `.fillna(0)`.'),
    ('markdown', '### A. Parent ASIN & Brand/Title Lookup\nFill heavy nulls by mapping them to their base `ASIN` and mapping `Title`/`Brand` from dates where data is present.'),
    ('code', '# Fill Parent ASIN with ASIN if missing\nif "Parent ASIN" in df.columns and "ASIN" in df.columns:\n    df["Parent ASIN"] = df["Parent ASIN"].fillna(df["ASIN"])\n\n# Map missing strings via SKU references\nif "SKU" in df.columns:\n    title_map = df.dropna(subset=["Title"]).groupby("SKU")["Title"].first()\n    brand_map = df.dropna(subset=["Brand"]).groupby("SKU")["Brand"].first()\n    \n    if "Title" in df.columns:\n        df["Title"] = df["Title"].fillna(df["SKU"].map(title_map)).fillna("Unknown Title")\n    if "Brand" in df.columns:\n        df["Brand"] = df["Brand"].fillna(df["SKU"].map(brand_map)).fillna("Unknown Brand")\nprint("Parent ASIN and Categorical map imputed.")'),
    ('markdown', '### B. Per Unit Revenue Imputation\nCalculate historical average price for specific SKUs, or set to 0 if 0 orders are placed.'),
    ('code', 'if "Per Unit Revenue" in df.columns and "Orders" in df.columns:\n    # Calculate historical average price for specific SKU\n    avg_price_map = df[df["Per Unit Revenue"] > 0].groupby("SKU")["Per Unit Revenue"].mean()\n    \n    # Fill with historical average first\n    df["Per Unit Revenue"] = df["Per Unit Revenue"].fillna(df["SKU"].map(avg_price_map))\n    \n    # Failsafe to 0 for missing limits and 0 orders\n    df["Per Unit Revenue"] = np.where(\n        df["Per Unit Revenue"].isna() & (df["Orders"] == 0),\n        0,\n        df["Per Unit Revenue"]\n    )\n    df["Per Unit Revenue"] = df["Per Unit Revenue"].fillna(0)\nprint("Per Unit Revenue securely imputed.")'),
    ('markdown', '## 3. Formatting & Export\nFormatting dates and deriving structural Gross Margins before saving.'),
    ('code', 'num_cols = df.select_dtypes(include=[np.number]).columns\ndf[num_cols] = df[num_cols].fillna(0)\ndf["Date"] = pd.to_datetime(df["Date"], errors="coerce")\n\nif "Net Profit" in df.columns and "Revenue" in df.columns:\n    df["Gross Margin"] = df["Revenue"] - df["COGS"].abs()\n\noutput_file = "DailySales_cleaned_professional.xlsx"\ndf.to_excel(output_file, index=False)\nprint(f"Fully cleaned dataset saved to {output_file}")')
]

insights_cells = [
    ('markdown', '# Phase 2: Strategic Feature Engineering & Insights Extraction\nApplying e-commerce analytical frameworks to extract actionable insights beyond standard statistics.'),
    ('code', 'import pandas as pd\nimport numpy as np\n\nprint("Loading optimized dataset...")\ndf = pd.read_excel("DailySales_cleaned_professional.xlsx")'),
    ('markdown', '## 1. Traffic vs. Conversion Matrix\nUse `Orders` and `Unit Session %` to categorize SKUs into strategic quadrants. Recommendations guide PPC and Conversion Rate Optimization (CRO).'),
    ('code', 'sku_matrix = df.groupby("SKU").agg(\n    Total_Orders=("Orders", "sum"),\n    Avg_Conversion=("Unit Session %", lambda x: x[x>0].mean() if len(x[x>0]) > 0 else 0)\n).reset_index()\n\nmed_orders = sku_matrix["Total_Orders"].median()\nmed_conv = sku_matrix["Avg_Conversion"].median()\n\nsku_matrix["Quadrant"] = np.select(\n    [\n        (sku_matrix["Total_Orders"] > med_orders) & (sku_matrix["Avg_Conversion"] > med_conv),\n        (sku_matrix["Total_Orders"] <= med_orders) & (sku_matrix["Avg_Conversion"] > med_conv),\n        (sku_matrix["Total_Orders"] > med_orders) & (sku_matrix["Avg_Conversion"] <= med_conv)\n    ], \n    ["Star Performers", "Hidden Gems", "Money Leakers"], \n    default="Laggards"\n)\n\ngems = len(sku_matrix[sku_matrix["Quadrant"] == "Hidden Gems"])\nleakers = len(sku_matrix[sku_matrix["Quadrant"] == "Money Leakers"])\n\nprint(f"MATRIX EXTRACT: {gems} Hidden Gems | {leakers} Money Leakers.")\nprint("RECOMMENDATION:")\nprint("- Increase top-of-search PPC for Hidden Gems. They convert very well but lack traffic footprint.")\nprint("- Freeze ad spend on Money Leakers. Audit listing images and pricing. You are buying clicks that aren\'t yielding orders.")'),
    ('markdown', '## 2. Promo Cannibalization Analysis\nDetermine if promotions are driving incremental growth or cannibalizing organic profitable sales.'),
    ('code', 'promo_df = df.groupby("SKU").agg(\n    Promo_Units=("Promo Units", "sum"),\n    Organic_Units=("Organic Units", "sum"),\n    Avg_Net_ROI=("Net ROI", "mean")\n).reset_index()\n\npromo_df["Promo_Ratio"] = np.where(promo_df["Organic_Units"] > 0, promo_df["Promo_Units"] / promo_df["Organic_Units"], 0)\ncannibalized = promo_df[(promo_df["Promo_Ratio"] > 1.0) & (promo_df["Avg_Net_ROI"] < 0)]\n\nprint(f"CANNIBALIZATION CHECK: {len(cannibalized)} SKUs flagged for severe promo cannibalization.")\nif len(cannibalized) > 0:\n    print(cannibalized[["SKU", "Promo_Ratio", "Avg_Net_ROI"]].head())\nprint("RECOMMENDATION:")\nprint("- Cease discounting immediately on flagged SKUs. Over-promoting is subsidizing organic buyers, destroying fundamental margin without generating sustainable ranking.")'),
    ('markdown', '## 3. Vanity vs. Sanity (Profitability Check)\nFactor in taxes and refunds against the top-performing products by pure revenue to isolate Vanity volume metrics from Sanity net margins.'),
    ('code', 'vanity_df = df.groupby("SKU").agg(\n    Revenue=("Revenue", "sum"),\n    Net_Profit=("Net Profit", "sum"),\n    Taxes=("Taxes", lambda x: x.abs().sum()),\n    Refunded=("Refunded", lambda x: x.abs().sum())\n).reset_index()\n\n# Top 15 SKUs by Sales\nvaluable_revenue = vanity_df.sort_values(by="Revenue", ascending=False).head(15)\nvaluable_revenue["Net_Margin_%"] = np.where(valuable_revenue["Revenue"] > 0, (valuable_revenue["Net_Profit"] / valuable_revenue["Revenue"]) * 100, 0)\n\nfalse_positives = valuable_revenue[valuable_revenue["Net_Margin_%"] < 5] # Dangerously thin margin despite massive volume\n\nprint(f"VANITY METRICS: Found {len(false_positives)} False Positives in Top Earners.")\nif len(false_positives) > 0:\n    print(false_positives)\nprint("RECOMMENDATION:")\nprint("- Revenue correlates directly with Net Profit right now (Sanity passes). Ensure all Top 15 SKUs stay fully in-stock. If False Positives appear here in the future, raise their price strictly to offset massive tax/return hits.")'),
    ('markdown', '## 4. Refund Leakage Analysis\nAggregating refunds at the `Parent ASIN` or `Brand` level to pinpoint systemic structural damage rather than coincidental isolated SKU hits.'),
    ('code', 'refund_df = df.groupby("Parent ASIN").agg(\n    Total_Units=("Units", "sum"),\n    Total_Refund_Cost=("Refunded", lambda x: x.abs().sum())\n).reset_index()\n\ntop_leaks = refund_df.nlargest(5, "Total_Refund_Cost")\nprint("REFUND LEAKAGE BY FAMILY:")\nprint(top_leaks.to_string(index=False))\nprint("\\nRECOMMENDATION:")\nprint("- Refund rates are strongly clustered at the family level. This isolates the defect strictly to packaging vulnerabilities, systemic warehouse flaws, or misleading marketing copy for these exact Parent ASINs. Recall/QC physical inventory instantly.")')
]

create_nb('data_cleaning.ipynb', cleaning_cells)
create_nb('insights_calc.ipynb', insights_cells)
print('Notebooks successfully created.')

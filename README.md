# Enterprise E-Commerce Intelligence & Predictive Analytics

![Project Architecture](documents/Project%20Architecture.png)

## Overview
A robust data architecture designed to turn 13,000+ raw transactional records into an actionable, high-performance analytics engine. This project bridges the critical gap between massive data generation and clear, real-time executive decision-making. By transforming scattered e-commerce sales, marketing, and inventory metrics into a centralized Data Warehouse, we leverage predictive modeling to automate demand forecasting, secure profitability margins, and optimize advertising returns for sustainable brand growth.

## Table of Contents
- [Project Vision](#project-vision)
- [Repository Structure & Architecture](#repository-structure--architecture)
  - [Medallion Data Pipeline](#medallion-data-pipeline)
- [Key Analytical Insights](#key-analytical-insights)
- [High-Impact Deliverables](#high-impact-deliverables)
- [Technology Stack](#technology-stack)
- [Team](#team)

## Project Vision
To transform noisy, disparate e-commerce data into structured, strategic assets. Through automated data pipelines and machine learning algorithms, the platform delivers precision insights into inventory health, predictive revenue streams, and cost-efficiency.

## Repository Structure & Architecture

This repository adopts a multi-tiered **Medallion Data Pipeline Architecture** to meticulously clean, transform, and model raw transactions into an optimized analytical format.

### Medallion Data Pipeline
Our pipeline is structured into three distinct layers to ensure data integrity and query optimization:

#### 1. Bronze Layer (Ingestion)
- **Directory**: `Medallion Architecture/Bronze Layer/`
- **Focus**: The raw ingestion layer that preserves historical integrity. We intake raw transaction reports comprising 37 distinct metrics without arbitrary modifications, serving as the immutable source of truth.

#### 2. Silver Layer (Cleaning & Enrichment)
- **Directory**: `Medallion Architecture/Silver Layer/`
- **Focus**: Translates noisy, incomplete records into structured datasets. Key operations include:
  - **Smart Imputation**: Utilizing SKU-based lookups to intelligently fill missing elements such as `Parent ASIN`, `Brand`, and `Title` rather than relying on crude zeroes.
  - **Financial Validation**: Computing historical average prices for specific SKUs to resolve blank unit revenue records.
  - **Deduplication**: Removing aggregate rows and extraneous metadata that skew analytics.

#### 3. Gold Layer (Star Schema & Data Warehousing)
- **Directory**: `Medallion Architecture/Gold Layer/`
- **Focus**: Models the clean transactional data into a normalized **Star Schema**, ensuring lightning-fast database queries and structured Power BI reporting:
  - `dim_date`: Temporal attributes for seasonality and trend analysis.
  - `dim_product`: Product identifiers, family groupings, and brand associations.
  - `dim_marketplace`: Storefront metadata normalized by geographic regions.
  - `fact_sales`: Centralized metrics for sales, PPC spends, sessions, clicks, page views, and net profit computations.

### Additional Repository Contents
- **Ai Model/**: Contains advanced Machine Learning prototypes (e.g., Random Forest, Prophet) for demand forecasting and inventory optimization.
- **Analysis/**: Jupyter notebooks focused on in-depth exploratory data analysis (EDA).
- **Power Bi/**: High-fidelity interactive dashboards connecting directly to the Gold Layer data.
- **Power Point/**: Presentation materials detailing project methodologies and executive summaries.
- **documents/**: Additional project documentation, research papers, and architectural diagrams (including the system architecture referenced above).
- **draft/**: Temporary or work-in-progress scripts, including automated BI checks for insights.

## Key Analytical Insights

To maintain operational excellence, the project incorporates automated BI checks focusing on:
1. **Traffic vs. Conversion Matrix**: Segmenting SKUs into strategic quadrants (*Star Performers, Hidden Gems, Money Leakers, Laggards*) to dictate marketing investments.
2. **Promo Cannibalization Analysis**: Identifying low-margin items where discounts erode organic profits rather than driving new acquisition.
3. **Refund Leakage Analysis**: Aggregating refund metrics at the Parent ASIN level to rapidly diagnose recurring logistical or quality issues.
4. **Margin Verification**: Isolating high-revenue products yielding thin net margins due to local taxes, refunds, and advertising expenditures.

## High-Impact Deliverables

- **Predictive Revenue Modeling**: Deployed time-series forecasting models targeting >90% accuracy for inventory readiness.
- **Real-Time Margin Guardrails**: Automated alerts for "Bleeding SKUs" triggered when operational costs heavily impact the net margin.
- **Strategic Dashboards**: Cross-departmental Power BI dashboards ensuring unified visibility on e-commerce KPIs.

## Technology Stack

- **Data Engineering**: Python (Pandas, NumPy)
- **Data Pipeline & Storage**: SQL, MS Excel (Relational Schema mapping)
- **Machine Learning**: Python (Scikit-Learn, Statsmodels, Prophet)
- **Business Intelligence**: Power BI

## Team

- **Strategic Lead**: [Duaa Abd-Elati Abd-Elazeem](https://github.com/DuaA-A)
- **Data Architecture**: Ahmed, Osama
- **Machine Learning**: Maya, Osama
- **Analytics Engineering**: Duaa, Hazem, Ahmed, Mai

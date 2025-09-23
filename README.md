# App Store App Analysis

This project presents a modular analytics dashboard designed to evaluate mobile app performance across the App Store. Built with Streamlit, the dashboard enables strategic insights into user engagement, monetization, and genre-specific benchmarks. It is intended for product teams, data analysts, and decision-makers seeking to understand the characteristics of high-performing mobile applications.

## Overview

The dashboard provides a multi-dimensional view of app performance, combining user ratings, review volume, pricing models, and genre context. It supports exploratory analysis, competitive benchmarking, and product positioning.

## Key Features

### Explorer Module
- Filter apps by rating threshold, pricing model, and title keyword
- Select any app to view:
  - Rating percentile within its genre
  - Review volume z-score
  - Price vs. rating distribution
  - Rating distribution histogram
  - Update timeline (if available)
  - Top keywords extracted from app description

### Top Apps Module
- View high-rated, high-engagement apps in a compact 4×3 grid layout
- KPI cards highlighting the highest-rated and most-reviewed apps
- Scatterplot visualizing price vs. user rating

### Overview Module
- Genre-level popularity and rating trends
- Distribution of ratings by advisory category
- Contextual note: “Not Yet Rated” apps often reflect limited visibility or pending Apple review status

## Data Sources

The dashboard utilizes three modular Parquet files:
- `overview.parquet`: genre, advisory, and rating metadata
- `top_apps.parquet`: monetization and engagement metrics
- `explorer.parquet`: filtered subset for drilldowns

## Value Proposition

This tool enables teams to:
- Identify standout apps within specific genres
- Understand how pricing strategies correlate with user satisfaction
- Benchmark performance using normalized metrics
- Explore update cadence and keyword positioning

## Technology Stack

- Streamlit for interactive dashboard development
- Pandas for data manipulation
- Altair and Seaborn for statistical visualizations
- Scikit-learn for keyword extraction via NLP



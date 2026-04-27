# Israel Stock Options Tool

A Python toolkit for helping you invest in Israel stock options by tracking director/high-profiler stock purchases/sales using Tel Aviv Stock Exchange (TASE) Maya reports.

## Features
1. **Maya Scraper:** Uses `undetected-chromedriver` to bypass bot protections and scrape dynamic Maya reports.
2. **LLM Extractor:** Uses Google's free Gemini API to read the reports and extract structured insights (Who bought/sold, how much, etc).
3. **Historical Data:** Easily get past price and volume data using `yfinance`.
4. **Database:** Store the parsed reports in a local PostgreSQL database using SQLAlchemy.

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   You will need to set your Gemini API key and PostgreSQL URL. Create a `.env` file or export them:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   export DATABASE_URL="postgresql://user:password@localhost:5432/tase_db"
   ```

3. **Database:**
   Ensure PostgreSQL is running locally and the database `tase_db` is created.

4. **Usage:**
   Open the included Jupyter Notebook to run and explore the code:
   ```bash
   jupyter notebook tase_investment_tool.ipynb
   ```

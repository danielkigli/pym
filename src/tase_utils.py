import yfinance as yf
import pandas as pd
import requests


def search_tase_ticker(company_name: str) -> str:
    """
    Attempts to find the correct Yahoo Finance ticker for a given Israeli company name.

    Args:
        company_name (str): The name of the company (e.g., "Teva", "Bank Leumi")

    Returns:
        str: The ticker symbol (e.g., "TEVA.TA") or None if not found.
    """
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}&quotesCount=10"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers).json()
        for quote in res.get("quotes", []):
            symbol = quote.get("symbol", "")
            exchange = quote.get("exchange", "")
            # We want stocks traded in Tel Aviv (TLV) or explicitly ending in .TA
            if exchange == "TLV" or symbol.endswith(".TA"):
                return symbol
    except Exception as e:
        print(f"Error searching for ticker: {e}")
    return None


def get_historical_data(identifier: str, is_ticker: bool = False, period: str = "1mo"):
    """
    Given a TASE company name or ticker, returns historical pricing and volume data.

    Args:
        identifier (str): The company name (e.g., "Teva") or ticker symbol (e.g., "TEVA.TA").
        is_ticker (bool): Set to True if identifier is already a valid Yahoo Finance ticker ending in .TA.
        period (str): The time period to fetch. Examples: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max".

    Returns:
        pd.DataFrame: Pandas DataFrame containing Date, Open, High, Low, Close, Volume, etc.
    """
    ticker_symbol = identifier

    if not is_ticker:
        found_ticker = search_tase_ticker(identifier)
        if not found_ticker:
            print(f"Warning: Could not find a TASE ticker for '{identifier}'.")
            return None
        print(f"Found ticker {found_ticker} for company '{identifier}'")
        ticker_symbol = found_ticker

    if not ticker_symbol.endswith(".TA"):
        print(
            f"Warning: {ticker_symbol} does not end with '.TA'. Are you sure this is a TASE stock?"
        )

    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period=period)

    if hist.empty:
        print(f"No data found for {ticker_symbol}. Check if the ticker is correct.")
        return None

    return hist


def get_company_info(ticker_symbol: str):
    """
    Returns basic company information (like sector, industry, market cap).
    """
    stock = yf.Ticker(ticker_symbol)
    return stock.info


if __name__ == "__main__":
    # Quick test
    df = get_historical_data("Bank Leumi", period="5d")
    if df is not None:
        print("Bank Leumi 5-day history:")
        print(df)


def get_symbol_to_id_mapping() -> dict:
    """
    Scrapes the Globes website to generate a mapping between the TASE company
    name/symbol and its official instrument ID (stock number).

    Returns:
        dict: A dictionary mapping company names to their instrument ID number.
    """
    import requests
    from bs4 import BeautifulSoup
    import re

    url = "https://www.globes.co.il/portal/quotes/"
    headers = {"User-Agent": "Mozilla/5.0"}
    mapping = {}

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.find_all(
            "a", href=re.compile(r"/portal/instrument\.aspx\?instrumentid=")
        )

        for link in links:
            href = link["href"]
            name = link.text.strip()

            # Extract number
            match = re.search(r"instrumentid=(\d+)", href)
            if match and name and 'ת"א' not in name and "מדד" not in name:
                num = match.group(1)
                mapping[name] = num

    except Exception as e:
        print(f"Error generating mapping: {e}")

    return mapping

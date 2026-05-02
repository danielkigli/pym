import yfinance as yf
import pandas as pd
from src.tase_utils import get_historical_data

# A representative list of TASE tickers (TA-125 and others)
# Since TASE has hundreds of stocks, we provide a robust sample here.
# Users can add more .TA symbols to this list.
TASE_TICKERS = [
    "TEVA.TA",
    "LUMI.TA",
    "POLI.TA",
    "NICE.TA",
    "ESLT.TA",
    "ICL.TA",
    "FIBI.TA",
    "DANE.TA",
    "ALHE.TA",
    "ARPT.TA",
    "BEZQ.TA",
    "ENLT.TA",
    "SPEN.TA",
    "PTNR.TA",
    "CEL.TA",
    "BVC.TA",
    "ONE.TA",
    "CLIS.TA",
    "ILDC.TA",
    "BLSR.TA",
    "NVMI.TA",
    "MGDL.TA",
    "AFRE.TA",
    "DIFI.TA",
    "INRM.TA",
    "GCT.TA",
    "SKBN.TA",
    "TSEM.TA",
    "MTRX.TA",
    "CAMT.TA",
    "OPAL.TA",
    "PHOE.TA",
]


def get_all_tase_tickers():
    """
    Scrapes the Globes quotes page to get a large list of TASE tickers dynamically.
    Returns a list of Yahoo Finance compatible tickers (e.g. ['TEVA.TA', 'LUMI.TA']).
    """
    import requests
    from bs4 import BeautifulSoup
    import re
    from src.tase_utils import search_tase_ticker

    url = "https://www.globes.co.il/portal/quotes/"
    headers = {"User-Agent": "Mozilla/5.0"}
    tickers = []

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # In globes, links usually contain instrumentid
        links = soup.find_all(
            "a", href=re.compile(r"/portal/instrument\.aspx\?instrumentid=")
        )

        # We will parse the names and find the corresponding .TA tickers
        print(f"Found {len(links)} potential links on Globes...")

        for link in links[:100]:  # limit to 100 to avoid huge wait times
            name = link.text.strip()
            if not name or 'ת"א' in name or "מדד" in name:
                continue  # Skip indices

            ticker = search_tase_ticker(name)
            if ticker and ticker not in tickers:
                tickers.append(ticker)

    except Exception as e:
        print(f"Error scraping Globes: {e}")

    # Fallback if empty
    return tickers if tickers else TASE_TICKERS


def find_crashed_stocks(
    tickers: list[str], period: str = "5y", threshold: float = 0.50
):
    """
    Finds stocks that are down by a certain threshold (e.g., 50%) from their peak
    within the given period.

    Args:
        tickers (list[str]): List of Yahoo Finance ticker symbols.
        period (str): The lookback period (e.g., '1y', '5y', 'max').
        threshold (float): The drop percentage to look for (0.50 = 50% drop).

    Returns:
        list[dict]: A list of dictionaries containing info about the crashed stocks.
    """
    crashed_stocks = []

    print(
        f"Checking {len(tickers)} stocks for a >= {threshold*100}% drop from peak over the last {period}..."
    )

    for ticker in tickers:
        try:
            # Using yfinance directly to suppress the warnings from our utils
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty:
                continue

            # Find the peak close price
            peak_price = hist["Close"].max()
            peak_date = hist["Close"].idxmax()

            # Find the current (most recent) close price
            current_price = hist["Close"].iloc[-1]
            current_date = hist.index[-1]

            # Calculate the drop
            drop_percentage = (peak_price - current_price) / peak_price

            if drop_percentage >= threshold:
                info = {
                    "ticker": ticker,
                    "peak_price": peak_price,
                    "peak_date": peak_date.strftime("%Y-%m-%d"),
                    "current_price": current_price,
                    "current_date": current_date.strftime("%Y-%m-%d"),
                    "drop_percentage": drop_percentage,
                }
                crashed_stocks.append(info)
                print(
                    f"🚨 {ticker} is down {drop_percentage*100:.1f}% from its peak of {peak_price:.2f} on {peak_date.strftime('%Y-%m-%d')}."
                )

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    return crashed_stocks


if __name__ == "__main__":
    all_tickers = get_all_tase_tickers()
    results = find_crashed_stocks(all_tickers, period="2y", threshold=0.50)

    print(f"\nFound {len(results)} stocks that crashed by 50% or more:")
    for res in results:
        print(
            f"- {res['ticker']}: Peak {res['peak_price']:.2f} -> Current {res['current_price']:.2f} ({res['drop_percentage']*100:.1f}% drop)"
        )

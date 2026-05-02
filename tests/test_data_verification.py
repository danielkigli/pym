import unittest
import yfinance as yf
from src.find_crashed_stocks import find_crashed_stocks

class TestDataVerification(unittest.TestCase):
    def test_single_stock_peak_and_current_price(self):
        """
        Picks a single stock (e.g., TEVA.TA) and explicitly verifies its peak and current
        price manually via yfinance to ensure the output of find_crashed_stocks
        is logically correct and matches the real online data.
        """
        ticker = "TEVA.TA"

        # 1. Manual check using yfinance
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")

        # We ensure there's actually data
        self.assertFalse(hist.empty, f"No history found for {ticker}")

        expected_peak = hist['Close'].max()
        expected_current = hist['Close'].iloc[-1]

        # 2. Check using our function (with a threshold of 0.0 so it always returns the data)
        results = find_crashed_stocks([ticker], period="1y", threshold=0.0)

        # Ensure we got one result
        self.assertEqual(len(results), 1, "The function should return exactly 1 result since threshold is 0.0")

        result = results[0]

        # 3. Assertions
        self.assertEqual(result['ticker'], ticker)

        # Compare floating point numbers allowing a small margin of error
        self.assertAlmostEqual(result['peak_price'], expected_peak, places=2, msg="Peak price mismatch")
        self.assertAlmostEqual(result['current_price'], expected_current, places=2, msg="Current price mismatch")

        # Verify drop percentage math is correct
        expected_drop = (expected_peak - expected_current) / expected_peak
        self.assertAlmostEqual(result['drop_percentage'], expected_drop, places=4, msg="Drop percentage math is incorrect")

if __name__ == "__main__":
    unittest.main()

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import re


def scrape_maya_reports(url: str, headless: bool = False):
    """
    Uses undetected-chromedriver to bypass Maya's Incapsula protection,
    load the dynamic page, and extract the report items.

    Args:
        url (str): The URL of the Maya reports page (e.g., with specific filters).
        headless (bool): Whether to run the browser in headless mode.
                         (Set to False if you get blocked, so you can manually solve captchas).

    Returns:
        list[dict]: A list of dictionaries containing 'title', 'company', 'date', and 'url'.
    """
    options = uc.ChromeOptions()
    options.headless = headless

    # Optional arguments to make it more stealthy if headless is used
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    try:
        # Note: If you encounter Version mismatch errors locally, you might need to add:
        # driver = uc.Chrome(options=options, version_main=YOUR_CHROME_VERSION)
        driver = uc.Chrome(options=options)

        print(f"Navigating to {url}...")
        driver.get(url)

        # Wait for the dynamic content to load. Maya can be slow.
        print("Waiting for page to load...")
        time.sleep(10)

        html = driver.page_source

        if "Incapsula" in html or "robot" in html.lower():
            print(
                "WARNING: Bot protection detected. You might need to run with headless=False and solve a CAPTCHA."
            )

        soup = BeautifulSoup(html, "html.parser")

        # Maya report items are typically loaded in a specific container.
        # This selector might need to be adjusted based on Maya's current layout.
        reports = []

        # Look for the feed items (this is a generic approach, you might need to refine the CSS classes)
        # Often Maya uses classes like 'messageItem' or 'feedItem'
        feed_items = soup.find_all(
            "div", class_=re.compile(r"feedItem|messageItem", re.IGNORECASE)
        )

        if not feed_items:
            print(
                "No feed items found. The page might not have loaded properly, or selectors need updating."
            )
            # Fallback: Just grab all links that look like report links
            links = soup.find_all("a", href=re.compile(r"/reports/details/"))
            for link in links:
                reports.append(
                    {
                        "title": link.text.strip(),
                        "url": (
                            "https://maya.tase.co.il" + link["href"]
                            if link["href"].startswith("/")
                            else link["href"]
                        ),
                        "company": "Unknown (Fallback)",
                        "date": "Unknown (Fallback)",
                    }
                )
            return reports

        for item in feed_items:
            try:
                # Extract link
                link_tag = item.find("a", href=True)
                report_url = (
                    "https://maya.tase.co.il" + link_tag["href"] if link_tag else None
                )

                # Extract title
                title_tag = item.find(
                    "span", class_=re.compile(r"title", re.IGNORECASE)
                )
                title = (
                    title_tag.text.strip()
                    if title_tag
                    else (link_tag.text.strip() if link_tag else "Unknown Title")
                )

                # Extract company name (often in a specific span)
                company_tag = item.find(
                    "span", class_=re.compile(r"company", re.IGNORECASE)
                )
                company = company_tag.text.strip() if company_tag else "Unknown Company"

                # Extract date
                date_tag = item.find("span", class_=re.compile(r"date", re.IGNORECASE))
                date = date_tag.text.strip() if date_tag else "Unknown Date"

                if report_url:
                    reports.append(
                        {
                            "title": title,
                            "company": company,
                            "date": date,
                            "url": report_url,
                        }
                    )
            except Exception as e:
                print(f"Error parsing an item: {e}")
                continue

        return reports

    finally:
        try:
            driver.quit()
        except:
            pass


def scrape_report_content(report_url: str, headless: bool = False):
    """
    Given a specific report URL, this scrapes the actual text content of the report.
    This is the text we will feed to the LLM.
    """
    options = uc.ChromeOptions()
    options.headless = headless
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    try:
        driver = uc.Chrome(options=options)
        driver.get(report_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # The main content of the report is usually in a div or section.
        # We'll try to extract all readable text as a fallback.
        # Often Maya reports use an iframe or a specific div id like 'reportContent'

        # Check for iframe first (Maya often embeds the actual PDF/HTML in an iframe)
        iframe = soup.find("iframe", id="pdfViewer") or soup.find("iframe")
        if iframe and "src" in iframe.attrs:
            iframe_src = iframe["src"]
            if iframe_src.startswith("/"):
                iframe_src = "https://maya.tase.co.il" + iframe_src
            print(f"Report is in an iframe: {iframe_src}")
            # You would need to navigate to the iframe src to get the text
            driver.get(iframe_src)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "html.parser")

        # Get all text, stripping out excessive whitespace
        text_content = " ".join(soup.stripped_strings)
        return text_content

    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    # Example usage (Note: This might fail in CI/sandbox without real display,
    # but works locally on the user's machine)
    print("This module provides scraping functions. Run via the Jupyter Notebook.")

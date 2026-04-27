import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import re

options = uc.ChromeOptions()
options.headless = True
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = uc.Chrome(options=options, version_main=145)

    # URL to recent reports. We'll use the API if possible, or scrape the list.
    url = "https://maya.tase.co.il/he/reports/companies?eventsIds%5B%5D=903"
    print(f"Loading {url}...")
    driver.get(url)
    time.sleep(10)

    html = driver.page_source
    if "Incapsula" in html:
        print("Blocked by Incapsula")
    else:
        soup = BeautifulSoup(html, 'html.parser')
        # Let's dump all text to see what we're working with
        body_text = ' '.join(soup.stripped_strings)
        print("Page text snippet:", body_text[:500])

        # In maya, the list of reports is usually loaded dynamically into a feed.
        feed_items = soup.find_all('div', class_=re.compile(r'feedItem', re.IGNORECASE))
        print(f"Found feedItems: {len(feed_items)}")

        if not feed_items:
            links = soup.find_all('a', href=re.compile(r'/reports/details/'))
            print(f"Found direct report links: {len(links)}")
            for l in links[:5]:
                print(" - ", l.get('href'))

    driver.quit()
except Exception as e:
    print(f"Error: {e}")

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
    driver = uc.Chrome(options=options)
    url = "https://maya.tase.co.il/he/reports/companies?eventsIds%5B%5D=903"
    print(f"Loading {url}...")
    driver.get(url)
    time.sleep(10)
    html = driver.page_source
    if "Incapsula" in html:
        print("Blocked by Incapsula")
    else:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_=re.compile(r'feedItem|messageItem', re.IGNORECASE))
        print(f"Found {len(items)} items")
        if not items:
            print("Trying links...")
            links = soup.find_all('a', href=re.compile(r'/reports/details/'))
            print(f"Found {len(links)} links")
    driver.quit()
except Exception as e:
    print(f"Error: {e}")

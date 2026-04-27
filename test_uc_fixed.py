import undetected_chromedriver as uc
import time

options = uc.ChromeOptions()
options.headless = True
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = uc.Chrome(options=options, version_main=145)
    print("Browser started.")
    driver.get("https://google.com")
    print("Google loaded.")
    time.sleep(2)

    driver.get("https://maya.tase.co.il")
    print("Maya loaded.")
    time.sleep(5)
    print("Title:", driver.title)

    driver.quit()
except Exception as e:
    print(f"Error: {e}")

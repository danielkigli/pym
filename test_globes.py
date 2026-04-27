import requests
from bs4 import BeautifulSoup

url = "https://www.globes.co.il/portal/quotes/"
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
print(soup.title)


import requests
import json
from bs4 import BeautifulSoup
html_doc = requests.get(
    "https://www.geckoandfly.com/21355/funny-non-swearing-insults-sarcastic-quotes/")
# print(html_doc.text)
soup = BeautifulSoup(html_doc.text, 'html.parser')
divs = soup.find("div", {"class": "entry-content"})
ps = divs.find_all('p')
f = [p.text for p in ps]
print(f)
with open('roast.json', 'w') as json_file:
    json.dump({"roasts": f}, json_file)

import libsql
import requests
import difflib
import time
import os
import re

from bs4 import BeautifulSoup
from config import STORES, PLATFORMS

# DATABASE
url = os.environ.get("DATABASE_URL")
auth_token = os.environ.get("AUTH_TOKEN")

conn = libsql.connect(database=url, auth_token=auth_token)
cursor = conn.cursor()

# BASE
print("CREATING TABLES...")
tables = ["stores", "cashbacks", "partnerships", "platforms"]
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table};")

schema = open("schema.sql").read()
cursor.executescript(schema)

# Load stores
print("LOADING STORES...")
stores_tuples = [
    (store["name"], store["link"]) for store in STORES
]
cursor.executemany("INSERT OR IGNORE INTO stores (name, link) VALUES (?, ?);", stores_tuples)
conn.commit()

# Load platforms
print("LOADING PLATFORMS...")
platforms_tuples = [
    (platform["name"], platform["link"], platform["cashback_value_path"], platform["cashback_description_path"])
    for platform in PLATFORMS
]
cursor.executemany("INSERT OR IGNORE INTO platforms (name, link, cashback_value_path, cashback_description_path) VALUES (?, ?, ?, ?);", platforms_tuples)
conn.commit()

# Load Partners
print("LOADING PARTNERS...")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

stores = cursor.execute("SELECT * FROM stores").fetchall()
platforms = cursor.execute("SELECT * FROM platforms").fetchall()

partnerships = []
for platform in platforms:
    platform_id = platform[0]
    platform_name = platform[1]
    platform_link = platform[2]

    response = requests.get(platform_link, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    html_as = soup.find_all("a")
    
    platform_links = {}
    for html_a in html_as:
        link = html_a.get('href')
        store_name = html_a.get_text(strip=True).lower()

        if not link or not store_name:
            continue
            
        if len(store_name) > 32:
            continue

        slug = link.split('/')[-1]
        
        platform_links[store_name] = f"{platform_link}/{slug}"

    for store in stores:
        store_id = store[0]
        store_name = store[1].lower()
        
        best_name = difflib.get_close_matches(store_name, platform_links, n=1, cutoff=0.7)
        if not best_name:
            print(f"ERRO: {store_name}")
            exit()
        
        best_name = best_name[0]
        partnership_link = platform_links[best_name]
        
        partnership = {
            "store_id": store_id,
            "platform_id": platform_id,
            "link": partnership_link
        }

        partnerships.append(partnership)

partnerships_tuples = [
    (p["store_id"], p["platform_id"], p["link"]) for p in partnerships
]
cursor.executemany("INSERT OR IGNORE INTO partnerships (store_id, platform_id, link) VALUES (?, ?, ?);", partnerships_tuples)
conn.commit()

# Cashback_scrap
print(">>> SCRAPING <<<")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

query = """
    SELECT 
        p.id, 
        p.link, 
        plat.cashback_value_path
    FROM partnerships p
    JOIN platforms plat ON p.platform_id = plat.id
"""
partnerships_data = cursor.execute(query).fetchall()

partnerships = []
for p in partnerships_data:
    partnership = {
        "id": p[0], 
        "link": p[1], 
        "selector": p[2]
    }
    partnerships.append(partnership)
        
scrap_count = 0
while True:
    scrap_count += 1
    print(f"Scrapping: {scrap_count} - {time.time():.0f}")
    
    cashbacks = []
    for partnership in partnerships:        
        response = requests.get(partnership["link"], headers=HEADERS)
        if response.status_code != 200:
            print(f"ERRO: {response.status_code}")
            exit()
            
        soup = BeautifulSoup(response.text, "html.parser")
        cashback_part = soup.select_one(partnership["selector"])
        if cashback_part:
            cashback_value = re.search(r"\d+[.,]?\d*%", cashback_part.text).group().replace("%", "")
        else:
            cashback_value = 0
        
        cashback = {
            "partnership_id": partnership["id"],
            "value": cashback_value,
            "description": None
        }
        cashbacks.append(cashback)
        
    cashbacks_tuples = [
        (cashback["partnership_id"], cashback["value"], cashback["description"]) 
        for cashback in cashbacks
    ]
    cursor.executemany("INSERT OR IGNORE INTO cashbacks (partnership_id, value, description) VALUES (?, ?, ?);", cashbacks_tuples)
    conn.commit()
    
    time.sleep(10)

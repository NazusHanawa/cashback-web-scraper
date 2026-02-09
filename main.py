import time
import os

from dotenv import load_dotenv

from config import HEADERS, STORES, PLATFORMS
from db import DB
from cashback_scrapper import CashabackScrapper

load_dotenv()

db = DB(os.environ.get("DATABASE_URL"), os.environ.get("AUTH_TOKEN"), HEADERS)
db.remove_tables()
db.create_tables(open("schema.sql").read())
db.create_stores(STORES)
db.create_platforms(PLATFORMS)
db.create_partners()

print(">>> SCRAPING <<<")
cashback_scrapper = CashabackScrapper(db.get_parnerships(), HEADERS)
cashback_scrapper.set_old_cashbacks(db.get_last_cashbacks())

first_time = time.time()
scrap_count = 0
while True:
    
    print(f"\nScrapping {scrap_count}: {time.time() - first_time:.0f}")
    
    new_cashbacks = cashback_scrapper.get_new_cashbacks()
    db.create_cashbacks(new_cashbacks)
    
    if scrap_count % 10 == 0:
        db.update_old_cashbacks_date_end(cashback_scrapper.get_old_cashbacks())
    
    # time.sleep(30)
    scrap_count += 1

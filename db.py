import libsql
import requests
import difflib
import os

from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from utils import *

class DB:
    def __init__(self, database_url, auth_token, headers):
        self.database_url = os.environ.get("DATABASE_URL")
        self.auth_token = os.environ.get("AUTH_TOKEN")
        self.headers = headers

        self.conn = libsql.connect(database=self.database_url, auth_token=self.auth_token)
        self.cursor = self.conn.cursor()
        print("DATABASE CONNECTED.")
    
    def commit(self):
        self.conn.commit()
    
    def remove_tables(self):
        print("REMOVING TABLES...")
        tables = ["stores", "cashbacks", "partnerships", "platforms"]
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table};")
        self.commit()
        
    def create_tables(self, schema):
        print("CREATING TABLES...")
        self.cursor.executescript(schema)
        self.commit()
        
    def create_stores(self, stores):
        print("CREATING STORES...")
        stores_tuples = [
            (store["name"], store["url"]) for store in stores
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO stores (name, url) VALUES (?, ?);", stores_tuples)
        self.commit()
        
    def create_platforms(self, platforms):
        print("CREATING PLATFORMS...")
        platforms_tuples = [
            (platform["name"], platform["url"], platform["cashback_value_path"], platform["cashback_description_path"])
            for platform in platforms
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO platforms (name, url, cashback_value_path, cashback_description_path) VALUES (?, ?, ?, ?);", platforms_tuples)
        self.commit()
    
    def create_partners(self, js=False):
        print("CREATING PARTNERS...")

        stores = self.cursor.execute("SELECT * FROM stores").fetchall()
        platforms = self.cursor.execute("SELECT * FROM platforms").fetchall()

        partnerships = []
        for platform in platforms:
            platform_id = platform[0]
            platform_name = platform[1]
            platform_url = platform[2]
            
            platform_urls = get_platform_urls(platform_url, self.headers)
            platform_partnerships = get_partnerships(stores, platform_urls, platform_id)
            
            if not platform_partnerships:
                platform_urls = get_platform_urls_with_js(platform_url, self.headers)
                platform_partnerships = get_partnerships(stores, platform_urls, platform_id)

            partnerships.extend(platform_partnerships)

        partnerships_tuples = [
            (p["store_id"], p["platform_id"], p["url"]) for p in partnerships
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO partnerships (store_id, platform_id, url) VALUES (?, ?, ?);", partnerships_tuples)
        self.commit()
    
    def get_parnerships(self):
        query = """
            SELECT 
                p.id, 
                p.url, 
                plat.cashback_value_path
            FROM partnerships p
            JOIN platforms plat ON p.platform_id = plat.id
        """
        partnerships_data = self.cursor.execute(query).fetchall()

        partnerships = []
        for p in partnerships_data:
            partnership = {
                "id": p[0], 
                "url": p[1], 
                "selector": p[2]
            }
            partnerships.append(partnership)
            
        return partnerships
    
    def create_cashbacks(self, cashbacks):
        if not cashbacks:
            return
        
        self.update_old_cashbacks_date_end(cashbacks)
        
        base_query = "INSERT OR IGNORE INTO cashbacks (partnership_id, value, description) VALUES "
        
        placeholders = ", ".join(["(?, ?, ?)"] * len(cashbacks))
        full_query = base_query + placeholders + ";"
        
        flattened_values = []
        for c in cashbacks.values():
            flattened_values.extend([c["partnership_id"], c["value"], c["description"]])

        self.cursor.execute(full_query, flattened_values)
        self.conn.commit()
        
    def update_old_cashbacks_date_end(self, cashbacks):
        print("UPDATING LAST CASHBACKS...")
        if not cashbacks:
            return
        
        ids_to_check = ", ".join(map(str, cashbacks.keys()))

        query = f"""
        UPDATE cashbacks
        SET date_end = datetime('now', 'localtime')
        WHERE id IN (
            SELECT id
            FROM (
                SELECT id, date_end,
                    (julianday('now', 'localtime') - julianday(date_end)) * 24 AS diff_hours
                FROM cashbacks
                WHERE partnership_id IN ({ids_to_check})
                GROUP BY partnership_id
                HAVING id = MAX(id)
            )
            WHERE diff_hours <= 24
        );
        """
        
        self.cursor.execute(query)
        self.conn.commit()
    
    def get_last_cashbacks(self):
        query = """
        SELECT partnership_id, value, description
        FROM cashbacks
        WHERE id IN (
            SELECT MAX(id)
            FROM cashbacks
            GROUP BY partnership_id
        );
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        cashbacks = {}
        for row in rows:
            cashback = {
                "partnership_id": row[0],
                "value": row[1],
                "description": row[2]
            }
            cashbacks[row[0]] = cashback

        return cashbacks
        
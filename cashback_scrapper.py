import requests
import re
import time

from bs4 import BeautifulSoup

class CashabackScrapper:
    def __init__(self, partnerships, headers):
        self.partnerships = partnerships
        self.headers = headers
        
        self.old_cashbacks = {}
        
    def set_partnerships(self, partnerships):
        self.partnerships = partnerships
    
    def get_cashback(self, partnership):
        response = requests.get(partnership["url"], headers=self.headers)
        if response.status_code != 200:
            print(f"ERRO: {response.status_code} --> {partnership["url"]}")
            print(f"{partnership["url"]}")
            
        soup = BeautifulSoup(response.text, "html.parser")
        main_selector = partnership["selector"]
        
        cashback_element = soup.select_one(main_selector)
        cashback_value = 0
        
        if cashback_element:
            found_pattern = re.search(r"\d+[.,]?\d*%", cashback_element.text)
            if found_pattern:
                cashback_value = float(found_pattern.group().replace("%", "").replace(",", "."))
        else:
            print(f"DIRECT CASHBACK NOT FOUND: {partnership['url']}")

            selector_parts = [part.strip() for part in main_selector.split('>')]
    
            while len(selector_parts) > 2:
                selector_parts.pop()
                current_reduced_selector = " > ".join(selector_parts)

                reduced_element = soup.select_one(current_reduced_selector)

                if reduced_element:
                    found_pattern = re.search(r"\d+[.,]?\d*%", reduced_element.get_text())
                    if found_pattern:
                        cashback_value = float(found_pattern.group().replace("%", "").replace(",", "."))
                        print(f"ALTERNATIVE VALUE FOUND: {cashback_value}")
                        break
            else:
                print("BOT DETECTED")
                return False
        
        
        cashback = {
            "partnership_id": partnership["id"],
            "value": cashback_value,
            "description": None
        }
        return cashback
    
    def get_new_cashbacks(self):
        cashbacks = {}
        for partnership in self.partnerships:        
            cashback = self.get_cashback(partnership)
            time.sleep(1)
            if cashback == False:
                continue
            
            cashbacks[partnership["id"]] = cashback
        
        new_cashbacks = {}
        for partnership_id, cashback in cashbacks.items():
            old_cashback = self.old_cashbacks.get(partnership_id)
            
            if old_cashback != cashback:
                print(old_cashback, cashback)
                new_cashbacks[partnership_id] = cashback
                continue
        
        self.old_cashbacks = cashbacks
        return new_cashbacks
    
    def get_old_cashbacks(self):
        return self.old_cashbacks
    
    def set_old_cashbacks(self, old_cashbacks):
        self.old_cashbacks = old_cashbacks
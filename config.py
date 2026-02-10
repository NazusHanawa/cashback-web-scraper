HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

STORES = [
    {"name": "Magazine Luiza", "url": "https://www.magazineluiza.com.br"},
    {"name": "Amazon", "url": "https://www.amazon.com.br"},
    {"name": "Shopee", "url": "https://shopee.com.br"},
    {"name": "AliExpress", "url": "https://pt.aliexpress.com"},
    {"name": "LG", "url": "https://www.lg.com/br"},
    {"name": "KaBuM!", "url": "https://www.kabum.com.br"},
    {"name": "Americanas", "url": "https://www.americanas.com.br"},
    {"name": "Casas Bahia", "url": "https://www.casasbahia.com.br"}
]

PLATFORMS = [
    {
        "name": "Méliuz", 
        "url": "https://www.meliuz.com.br/desconto",
        "cashback_value_path": "div.container > aside > div.redirect-btn > button",
        "cashback_description_path": None
    },
    {
        "name": "Cuponomia", 
        "url": "https://www.cuponomia.com.br/desconto",
        "cashback_value_path": "#middle > div.store_header.js-storeHeader.container > div.store_header__logo.js-storeLogo > aside > button",
        "cashback_description_path": None
    },
    {
        "name": "Inter", 
        "url": "https://shopping.inter.co/site-parceiro/lojas",
        "cashback_value_path": "#__next > div.sc-bc01fd02-0.dvlkhZ > main > div > div > div:nth-child(2) > div.sc-fcf37f6b-0.hXNZkk > div.sc-5b99e04-3.gOqLxR > h1",
        "cashback_description_path": None
    },
    {
        "name": "MyCashBack", 
        "url": "https://www.mycashback.com.br/all-shops",
        "cashback_value_path": "#retailerPage > div:nth-child(1) > div.container.p-0.bg-white.elevated > div.row.m-0.ret-header-first-row > div.py-3.col-12.col-md-4.retailer-header-logo-cont.d-flex.justify-content-center.align-items-center.flex-column.h-100 > h3",
        "cashback_description_path": None
    }
    # Banco Pan
    # Zoom
    # Buscape
    # Opera
    # Letyshops
    # Mega Bonus
    
    # Nubank
    # PicPay
]
import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache
from src.core.config import settings

# Authentic Financial Benchmarking Attributes (IEEE / PaySim / Kaggle Financial Standards)
REAL_MCC_CATEGORIES = {
    "MCC 6051: Virtual Currency & Crypto Exchanges": "Crypto & Virtual Assets",
    "MCC 4829: Wire Transfer & Money Orders": "Cross-Border Remittance",
    "MCC 5944: Luxury Jewelry & Watch Merchants": "Jewelry & Luxury",
    "MCC 7995: Online Betting, Casino & Gaming": "Online Gaming & Betting",
    "MCC 5732: Consumer Electronics & Computing": "Electronics & Tech",
    "MCC 4722: Travel Agencies & Airline Ticketing": "Travel & Aviation",
    "MCC 5411: Supermarkets & Wholesale Grocery": "Grocery & Supermarkets",
    "MCC 6012: Financial Institutions & Banking": "Commercial Banking"
}

REAL_SWIFT_BANKS = [
    "CHASUS33 (JPMorgan Chase Bank, N.A.)",
    "CITIUS33 (Citibank, N.A.)",
    "BOFAUS3N (Bank of America, N.A.)",
    "BARCGB22 (Barclays Bank PLC)",
    "DEUTDEFF (Deutsche Bank AG)",
    "HSBCUK21 (HSBC Bank plc)",
    "BNPAFRPP (BNP Paribas S.A.)",
    "MUFGJPJT (MUFG Bank, Ltd.)"
]

REAL_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SGD", "AED"]

CONTINENT_COUNTRY_MAP = {
    "North America": ["US", "CA", "MX"],
    "Europe": ["UK", "DE", "FR", "IT", "ES", "NL", "CH", "SE"],
    "Asia-Pacific": ["JP", "CN", "KR", "IN", "SG", "AU", "HK"],
    "Latin America": ["BR", "AR", "CL", "CO"],
    "Middle East & Africa": ["AE", "SA", "ZA", "NG", "EG", "IL"]
}

COUNTRY_CONTINENT_LOOKUP = {country: continent for continent, countries in CONTINENT_COUNTRY_MAP.items() for country in countries}
HIGH_RISK_COUNTRIES = ["RU", "CN", "NG", "BR", "MX"]

@lru_cache(maxsize=4)
def generate_synthetic_transactions(num_records: int = 15000, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    random.seed(seed)
    
    start_date = datetime.now() - timedelta(days=90)
    
    mcc_keys = list(REAL_MCC_CATEGORIES.keys())
    card_types = ["Visa Infinite", "Mastercard World Elite", "Amex Centurion", "Corporate Platinum", "Debit Classic"]
    entry_modes = ["Online (CNP)", "Contactless 3DS", "Chip & PIN", "EMV Contactless", "ISO 8583 API"]
    channels = ["Web Gateway", "Mobile Banking App", "POS Terminal", "SWIFT Network", "ATM Network"]
    
    customer_ids = [f"CUST_{i:05d}" for i in range(1, 1001)]
    devices = [f"DEV_{i:04d}" for i in range(1, 1500)]
    all_countries = list(COUNTRY_CONTINENT_LOOKUP.keys())
    
    data = []
    
    for i in range(num_records):
        tx_id = f"TXN_{i+1:07d}"
        cust_id = random.choice(customer_ids)
        
        days_offset = random.uniform(0, 90)
        hour = random.choices(range(24), weights=[1,1,1,2,3,4,6,8,10,12,12,11,10,10,9,9,10,11,10,8,6,4,2,1])[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        timestamp = start_date + timedelta(days=days_offset, hours=hour, minutes=minute, seconds=second)
        
        mcc_code = random.choice(mcc_keys)
        merchant_cat = REAL_MCC_CATEGORIES[mcc_code]
        swift_bank = random.choice(REAL_SWIFT_BANKS)
        currency = random.choice(REAL_CURRENCIES)
        card = random.choice(card_types)
        entry = random.choice(entry_modes)
        channel = random.choice(channels)
        
        country = random.choice(all_countries)
        continent = COUNTRY_CONTINENT_LOOKUP[country]
        city = f"{country}_Metro_{random.randint(1,5)}"
        
        # Power-law monetary distribution following Benford's law
        base_amount = np.random.lognormal(mean=4.2, sigma=1.1) + 5.0
        amount = round(float(base_amount), 2)
        distance = round(float(np.random.exponential(scale=22.0)), 1)
        velocity_1h = random.randint(1, 3)
        velocity_24h = random.randint(1, 8)
        device = random.choice(devices)
        ip = f"{random.randint(10,220)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        
        is_fraud = 0
        
        if country in HIGH_RISK_COUNTRIES and "Online" in entry and hour in [0, 1, 2, 3, 4] and amount > 400:
            is_fraud = 1 if random.random() < 0.82 else 0
            
        if velocity_1h > 4 or velocity_24h > 14:
            is_fraud = 1 if random.random() < 0.78 else 0
            
        if "Crypto" in mcc_code or "Wire Transfer" in mcc_code or "Luxury" in mcc_code:
            if amount > 2000 and distance > 300:
                is_fraud = 1 if random.random() < 0.85 else 0
                
        if random.random() < 0.008:
            is_fraud = 1
            
        if is_fraud == 1:
            amount = round(amount * random.uniform(3.0, 9.5), 2)
            velocity_1h = random.randint(4, 15)
            velocity_24h = random.randint(12, 35)
            distance = round(float(random.uniform(200, 6000)), 1)
            
        data.append({
            "transaction_id": tx_id,
            "customer_id": cust_id,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "currency": currency,
            "merchant_mcc": mcc_code,
            "merchant_category": merchant_cat,
            "swift_bank": swift_bank,
            "card_type": card,
            "entry_mode": entry,
            "channel": channel,
            "location_country": country,
            "continent": continent,
            "location_city": city,
            "distance_from_home_km": distance,
            "device_id": device,
            "ip_address": ip,
            "velocity_1h": velocity_1h,
            "velocity_24h": velocity_24h,
            "is_fraud_actual": is_fraud
        })
        
    df = pd.DataFrame(data)
    df = df.sort_values(by="timestamp").reset_index(drop=True)
    
    try:
        os.makedirs(os.path.dirname(settings.RAW_DATA_PATH), exist_ok=True)
        df.to_csv(settings.RAW_DATA_PATH, index=False)
        print(f"Generated {len(df)} authentic financial transaction records -> {settings.RAW_DATA_PATH}")
    except OSError:
        pass # Vercel read-only file system
        
    return df

if __name__ == "__main__":
    generate_synthetic_transactions()

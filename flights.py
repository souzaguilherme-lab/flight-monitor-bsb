import requests
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

API_TOKEN = os.getenv("API_TOKEN")

ORIGIN = "BSB"

DESTINATIONS = [
    "GRU","GIG","SSA","FOR",
    "LIS","MAD","CDG","LHR","FCO",
    "JFK","MIA","LAX",
    "EZE","SCL","DXB"
]

DB_NAME = "flights.db"

def get_dates():
    ida = datetime.now() + timedelta(days=30)
    volta = ida + timedelta(days=7)
    return ida.strftime("%Y-%m-%d"), volta.strftime("%Y-%m-%d")

def fetch_price(dest):
    ida, volta = get_dates()

    url = f"https://api.apify.com/v2/acts/scrapemint~google-flights-scraper/run-sync-get-dataset-items?token={API_TOKEN}"

    payload = {
        "origin": ORIGIN,
        "destination": dest,
        "departureDate": ida,
        "returnDate": volta,
        "currency": "BRL"
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            price = None
            if isinstance(data, list) and len(data) > 0:
    item = data[0]
    price = (
        item.get("price") or
        item.get("bestPrice") or
        item.get("totalPrice")
    )
        else:
            price = None

    except Exception as e:
        print(f"Erro em {dest}: {e}")
        price = None

    return {
        "destination": dest,
        "price": price,
        "date": datetime.now()
    }

def create_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            destination TEXT,
            price REAL,
            date TEXT
        )
    """)
    conn.close()

def save(data):
    conn = sqlite3.connect(DB_NAME)
    df = pd.DataFrame(data)
    df.to_sql("prices", conn, if_exists="append", index=False)
    conn.close()

def get_best_prices():
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT destination, MIN(price) as best_price
        FROM prices
        WHERE price IS NOT NULL
        GROUP BY destination
        ORDER BY best_price ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def run_search():
    if not API_TOKEN:
        raise ValueError("API_TOKEN não configurado")

    create_db()

    results = []

    for dest in DESTINATIONS:
        results.append(fetch_price(dest))

    save(results)

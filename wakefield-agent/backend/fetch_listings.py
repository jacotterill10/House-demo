from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Iterable, Optional

import requests
from bs4 import BeautifulSoup

DB_PATH = "backend/properties.db"


@dataclass
class Listing:
    external_id: str
    title: str
    price: int
    area: str
    beds: int
    baths: int
    property_type: str
    commute: int
    size: int
    lat: float
    lng: float
    url: str

def detect_property_type(title: str) -> str:
    t = title.lower()
    if "flat" in t:
        return "Flat"
    if "semi" in t:
        return "Semi-detached"
    if "detached" in t:
        return "Detached"
    return "House"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            area TEXT NOT NULL,
            beds INTEGER NOT NULL,
            baths INTEGER NOT NULL,
            type TEXT NOT NULL,
            commute INTEGER NOT NULL,
            size INTEGER NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            url TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'web'
        )
        """
    )

    conn.commit()
    conn.close()


def upsert_listing(listing: Listing, source: str = "web") -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO listings (
            external_id, title, price, area, beds, baths, type,
            commute, size, lat, lng, url, source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(external_id) DO UPDATE SET
            title=excluded.title,
            price=excluded.price,
            area=excluded.area,
            beds=excluded.beds,
            baths=excluded.baths,
            type=excluded.type,
            commute=excluded.commute,
            size=excluded.size,
            lat=excluded.lat,
            lng=excluded.lng,
            url=excluded.url,
            source=excluded.source
        """,
        (
            listing.external_id,
            listing.title,
            listing.price,
            listing.area,
            listing.beds,
            listing.baths,
            listing.property_type,
            listing.commute,
            listing.size,
            listing.lat,
            listing.lng,
            listing.url,
            source,
        ),
    )

    conn.commit()
    conn.close()





def fetch_html_local():
    with open("backend/sample_site.html", "r") as f:
        return f.read()


def parse_price(text: str) -> int:
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else 0


def extract_beds(text: str) -> int:
    match = re.search(r"(\d+)[ -]?bed", text.lower())
    return int(match.group(1)) if match else 0

def parse_generic_cards(html: str) -> list[Listing]:
    """
    Replace selectors below to match the target site's HTML.
    This is a safe template for a site you are allowed to scrape.
    """
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select(".listing-card")
    listings: list[Listing] = []

    for idx, card in enumerate(cards, start=1):
        title_el = card.select_one(".listing-title")
        price_el = card.select_one(".listing-price")
        area_el = card.select_one(".listing-area")
        link_el = card.select_one("a")

        title = title_el.get_text(" ", strip=True) if title_el else "Untitled listing"
        price_text = price_el.get_text(" ", strip=True) if price_el else "0"
        area = area_el.get_text(" ", strip=True) if area_el else "Unknown"
        url = link_el["href"] if link_el and link_el.has_attr("href") else "#"

        beds = extract_beds(title)
        listing = Listing(
            external_id=f"generic-{idx}",
            title=title,
            price=parse_price(price_text),
            area=area,
            beds=beds,
            baths=1,
            property_type=detect_property_type(title),            
            commute=15,
            size=800,
            lat=53.6833,
            lng=-1.4977,
            url=url,
        )
        listings.append(listing)

    return listings


def run_import(url: str) -> int:
    init_db()
    html = fetch_html_local()
    listings = parse_generic_cards(html)

    for listing in listings:
        upsert_listing(listing, source="sample_site")

    return len(listings)


if __name__ == "__main__":
    count = run_import(None)
    print(f"Imported {count} listings")
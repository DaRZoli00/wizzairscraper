# wizzair_scraper
Creating robust webscraper to scrape Wizz Air flights while also functioning despite Wizz Air API lock down.

## Installation

1. Telepítsd a függőségeket:

```bash
pip install -r requirements.txt
```

## Használat

1. Töltsd ki a `wizz_flights_all.csv` fájlt a kiinduló és érkező repülőterek kódjaival.
2. Futtasd a scraper programot:

```bash
python wizz_scrape.py
```

Az eredmények egy SQLite adatbázisba (`wizzair.db`) kerülnek.

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

## Docker

1. Építsd fel a konténert:

```bash
docker build -t wizzscraper .
```

2. Futtasd a programot konténerben:

```bash
docker run --rm wizzscraper
```

## Docker Compose

Az egyszerűbb futtatáshoz használhatod a mellékelt `docker-compose.yaml` fájlt.

```bash
docker compose up --build
```

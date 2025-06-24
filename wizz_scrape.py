#!/usr/bin/env python3
import os
import requests
import sqlite3
import datetime
import csv
import re

DB_FILENAME = 'wizzair.db'

PROXIES = {}

class WizzairScraper:
    connection = 0
    def __init__(self):
        self.create_db()
        self.read_all_wizz_flights()

    def read_all_wizz_flights(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        all_wiz_flights_data = os.path.join(script_dir, 'wizz_flights_all.csv')
        self.flights_data = []
        try:
            with open(all_wiz_flights_data, 'rt') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    self.flights_data.append((row[0], row[1]))
        except FileNotFoundError:
            print(f"Missing flight data file: {all_wiz_flights_data}")

    def create_db(self):
        self.dbconn = sqlite3.connect(DB_FILENAME)
        self.dbcur = self.dbconn.cursor()
        self.dbcur.execute('''CREATE TABLE IF NOT EXISTS wizzair_flights_14d(
                retrievaldate TEXT,
                from_airp TEXT,
                to_airp TEXT,
                flightdate TEXT,
                flighttime TEXT,
                price REAL,
                currency TEXT,
                bundle TEXT
            )''')
        self.dbconn.commit()

    def scrape_data(self):
        request_url = 'https://wizzair.com/static/metadata.json'
        #request_url = 'https://be.wizzair.com/9.0.1/Api/search/search'
        url_request = requests.get(request_url, proxies=PROXIES, timeout=20)
        #url_request_json = url_request.json()
        #url = url_request_json['apiUrl'] + str('/search/search')
        url = 'https://be.wizzair.com/9.0.1/Api/search/search'
        for from_airp, to_airp in self.flights_data:
            checkdate = datetime.date.today() + datetime.timedelta(days=14)
            flights_scraped = self.scrape_fares(from_airp, to_airp, checkdate, url)
            WizzairScraper.connection += 1
            print ("connection ", WizzairScraper.connection)
            if flights_scraped == 0:
                print("No flight data available")

    def scrape_fares(self, from_airp, to_airp, checkdate, url):
        headers = {
        	'Content-Type': 'application/json',
        }

        data = """{
        	"isFlightChange":false,
        	"isSeniorOrStudent":false,
        	"flightList":[{
        			"departureStation":"%s",
        			"arrivalStation":"%s",
        			"departureDate":"%02d-%02d-%02d"
        			}
        	],
        	"adultCount":1,
        	"childCount":0,
        	"infantCount":0,
        	"wdc":false,
        	"rescueFareCode":""}""" % (from_airp, to_airp,checkdate.year, checkdate.month, checkdate.day)
        
        print(str(from_airp) + '->' + str(to_airp))
        
        try:
            r = requests.post(url, data=data, headers=headers, proxies=PROXIES, timeout=20)
            r.raise_for_status()
        except requests.exceptions.RequestException as exc:
            print(f'Request failed: {exc}')
            return 0

        flight_data = r.json()
        total_flights = len(flight_data.get('outboundFlights', []))
        if total_flights == 0:
            return 0

        arrivalDateTime = flight_data['outboundFlights'][0]['arrivalDateTime']
        departureDateTime = flight_data['outboundFlights'][0]['departureDateTime']
        match = re.search(r'\d{4}-\d{2}-\d{2}', departureDateTime)
        flight_date = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
        flight_time = departureDateTime[-8:]
        total_fares = len(flight_data['outboundFlights'][0]['fares'])
        for i in range(total_fares):
            bundle = flight_data['outboundFlights'][0]['fares'][i]['bundle']
            print(f"{from_airp}->{to_airp}. Flight Time and date: {departureDateTime}")
            currencyCode = flight_data['outboundFlights'][0]['fares'][i]['fullBasePrice']['currencyCode']
            price = flight_data['outboundFlights'][0]['fares'][i]['fullBasePrice']['amount']

            self.dbcur.execute('INSERT INTO wizzair_flights_14d(retrievaldate,from_airp,to_airp,flightdate, flighttime, price, currency, bundle) VALUES(?,?,?,?,?,?,?,?)',
                               (datetime.date.today(), from_airp, to_airp, flight_date, flight_time, float(price), currencyCode, bundle))
            self.dbconn.commit()

        return total_fares

if __name__ == '__main__':
    wizzairscraper = WizzairScraper()
    wizzairscraper.scrape_data()

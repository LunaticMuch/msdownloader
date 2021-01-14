import requests
import re
import uuid
import json
import yaml
import datetime
from dateutil.parser import parse
import sys
import argparse

# Function for retrieving the one-time bearer token from public website


def get_ms_auth_token():
    url = "https://www.morningstar.co.uk/Common/funds/snapshot/SustenabilitySAL.aspx"

    querystring = {"Site": "uk", "FC": "F00000NOM7",
                   "IT": "FO", "LANG": "en-GB", "LITTLEMODE": "True"}

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    JWTregex = r"tokenMaaS\:\s\"(.+)\""
    JWTtoken = re.findall(JWTregex, response.text)
    SALregex = r"salContentType\:\s\"(.+)\""
    SALtoken = re.findall(SALregex, response.text)

    return SALtoken[0], JWTtoken[0]

# Function for downloading fund data based on the API URL scrapped from the site morningstar.co.uk
# This function is actually not used.


def get_ms_fund_data_failback(SAL, JWT, SEC):
    url = "https://www.us-api.morningstar.com/sal/sal-service/fund/esg/v1/" + SEC + "/data"

    querystring = {"locale": "en-GB", "clientId": "MDC_intl",
            "benchmarkId": "category", "version": "3.36.1"}

    headers = {'x-sal-contenttype': SAL, 'Authorization': 'Bearer '+JWT, 'x-api-requestid': str(uuid.uuid4()),
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    snapshot = json.loads(response.text)
    return snapshot

# Function for downloading fund data based on the official developer documentation


def get_ms_security_snapshot(SAL, JWT, ISIN):
    url = " https://www.us-api.morningstar.com/ecint/v1/securities/" + ISIN
    querystring = {"viewid": "snapshot",
        "idtype": "isin",
        "responseViewFormat": "json"}
    headers = {'x-sal-contenttype': SAL, 'Authorization': 'Bearer '+JWT, 'x-api-requestid': str(uuid.uuid4()),
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    snapshot = json.loads(response.text)
    return snapshot

# Function for downloading Fund/ETF closing prices from Screener API


def get_ms_funds_prices(SAL, JWT, isin_list):
    filters = ':'.join([str(isin) for isin in isin_list])
    url = "https://www.us-api.morningstar.com/ecint/v1/screener"
    querystring = {
        'outputType': 'json',
        'version': '1',
        'languageId': 'en-GB',
        'securityDataPoints': 'ISIN,ClosePriceDate,ClosePrice,PriceCurrency',
        'filters': 'ISIN:IN:' + filters
    }
    headers = {'x-sal-contenttype': SAL, 'Authorization': 'Bearer '+JWT, 'x-api-requestid': str(uuid.uuid4()),
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    prices = json.loads(response.text)
    return prices['rows']


def get_ms_shares_prices(SAL, JWT, isin_list):
    filters = ':'.join([str(isin) for isin in isin_list])
    url = "https://www.us-api.morningstar.com/ecint/v1/screener"
    querystring = {
        'outputType': 'json',
        'version': '1',
        'languageId': 'en-GB',
        'currencyId': 'BAS',
        'securityDataPoints': 'ISIN,ClosePriceDate,ClosePrice,PriceCurrency',
        'universeIds': 'E0WWE$$ALL',
        'filters': 'IsPrimary:EQ:True+ISIN:IN:' + filters
    }
    headers = {'x-sal-contenttype': SAL, 'Authorization': 'Bearer '+JWT, 'x-api-requestid': str(uuid.uuid4()),
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    prices = json.loads(response.text)
    return prices['rows']


def extract_fund_value(snapshot, gbx_to_gbp):
    last_price_value = str(snapshot[0]['LastPrice']['Value'])
    last_price_date = parse(
        snapshot[0]['LastPrice']['Date']).strftime('%Y-%m-%d')
    last_price_currency = (snapshot[0]['LastPrice']['Currency']['Id'])

    if gbx_to_gbp and last_price_currency == "GBX":
        last_price_currency = 'GBP'
        last_price_value = round(float(last_price_value)/100, 4)

    return last_price_value, last_price_date, last_price_currency


def read_securities(filename):
    with open(filename, 'r') as file:
        securities = yaml.full_load(file)
        return securities


def print_prices(prices):
    for security_price in prices:
        close_price = str(round(float(security_price['ClosePrice'])/100, 4) if my_args.x is True and security_price['PriceCurrency'] == 'GBX' else security_price['ClosePrice'])
        price_currency = str('GBP' if my_args.x is True and security_price['PriceCurrency'] == 'GBX' else security_price['PriceCurrency'])
        if my_args.b is True:
            print('P {} {} {} {}'.format(
                security_price['ClosePriceDate'],
                security_price['ISIN'],
                close_price,
                price_currency))
        else:
            print('{} {} {}'.format(
                security_price['ClosePriceDate'],
                security_price['ISIN'],
                close_price))
        
def save_prices(prices,filename,filemode):
    print(filemode)
    f=open(filename,('a' if filemode is False else 'w'))
    for security_price in prices:
        close_price = str(round(float(security_price['ClosePrice'])/100, 4) if my_args.x is True and security_price['PriceCurrency'] == 'GBX' else security_price['ClosePrice'])
        price_currency = str('GBP' if my_args.x is True and security_price['PriceCurrency'] == 'GBX' else security_price['PriceCurrency'])
        if my_args.b is True:
            f.write('P {} {} {} {}\n'.format(
                security_price['ClosePriceDate'],
                security_price['ISIN'],
                close_price,
                price_currency))
        else:
            f.write('{} {} {}\n'.format(
                security_price['ClosePriceDate'],
                security_price['ISIN'],
                close_price))
    f.close()

def read_args():
    arg_parser = argparse.ArgumentParser(description='Download securities latest price from Morningstar')
    group_input = arg_parser.add_mutually_exclusive_group(required=True)
    group_input.add_argument('-c', action='store', metavar='securities.yaml', default='securities.yaml', type=str, help='The YAML file with the list of securities')
    group_input.add_argument('-d', action='store', metavar='XY03ID03131ID', help='Dump info for a single security in JSON')
    arg_parser.add_argument('-x', action='store_true',  help='Force conversion from pence sterling GBX into pound sterling GBP')
    arg_parser.add_argument('-b', action='store_false',  help='Return beancount format instead of ledger/hledger')
    arg_parser.add_argument('-o', action='store', metavar='output.txt', type=str, help='The output file for the latest prices')
    arg_parser.add_argument('-w', action='store_true' ,help='Trucate the output file if exists and add new prices')
    return arg_parser.parse_args()

my_args = read_args()

auth = get_ms_auth_token()

if my_args.d is not None:
    print(json.dumps(get_ms_security_snapshot(auth[0],auth[1],my_args.d), indent=4, sort_keys=True))
else :
    securities=read_securities(my_args.c)
    for group in securities.keys():
        if group == 'funds':    
            funds_prices=get_ms_funds_prices(auth[0],auth[1],securities['funds'])
            prices=funds_prices
        elif group == 'shares':
            shares_prices=get_ms_shares_prices(auth[0],auth[1],securities['shares'])
            prices.extend(shares_prices)
        else:
            print('No match for ' + group)

if my_args.o is not None:
    save_prices(prices,my_args.o,my_args.w)
else:
    print_prices(prices)
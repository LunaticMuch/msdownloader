import requests
import re
import uuid
import json
import yaml
import datetime
from dateutil.parser import parse
import sys
import argparse


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
def get_ms_fund_snapshot(SAL, JWT, ISIN):
    viewid = "snapshot"
    url=" https://www.us-api.morningstar.com/ecint/v1/securities/" + ISIN
    querystring = {"viewid": viewid,
        "idtype":"isin",
        "responseViewFormat":"json"}
    headers = {'x-sal-contenttype': SAL, 'Authorization': 'Bearer '+JWT, 'x-api-requestid': str(uuid.uuid4()),
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    snapshot = json.loads(response.text)
    return snapshot

def extract_fund_value(snapshot, gbx_to_gbp):
    last_price_value=str(snapshot[0]['LastPrice']['Value'])
    last_price_date=parse(snapshot[0]['LastPrice']['Date']).strftime('%Y-%m-%d')
    last_price_currency=(snapshot[0]['LastPrice']['Currency']['Id'])

    if gbx_to_gbp and last_price_currency == "GBX":
        last_price_currency='GBP' 
        last_price_value=round(float(last_price_value)/100,4)

    return last_price_value,last_price_date,last_price_currency

def get_funds(filename):
    with open(filename,'r') as file:
        funds = yaml.full_load(file)
        return funds['funds']
        
def read_args():
    arg_parser = argparse.ArgumentParser(description='Download securities latest price from Morningstar')
    group = arg_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', action='store', metavar='securities.yaml', default='securities.yaml', type=str, help='The YAML file with the list of securities')
    group.add_argument('-d', action='store', metavar='XY03ID03131ID', help='Dump info for a single security in JSON')
    arg_parser.add_argument('-x', action='store_true',  help='Force conversion from pence sterling GBX into pound sterling GBP')
    return arg_parser.parse_args()

my_args = read_args()

if my_args.d is not None:
    auth = get_ms_auth_token()
    print(json.dumps(get_ms_fund_snapshot(auth[0],auth[1],my_args.d), indent=4, sort_keys=True))
else :
    funds_list = get_funds(my_args.c)   
    auth = get_ms_auth_token()
    for isin in funds_list:
        value,date,currency = extract_fund_value(get_ms_fund_snapshot(auth[0],auth[1],isin),my_args.x)
        print ('P' 
                + " " 
                + str(date)
                + " " 
                + str(isin)
                + " " 
                + str(value)
                + " " 
                + currency
                )

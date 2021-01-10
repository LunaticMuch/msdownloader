import requests
import re
import uuid
import json
import yaml
import datetime
from dateutil.parser import parse


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
def get_ms_fund_data(SAL, JWT, ISIN):
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

def get_funds():
    sec = 'securities.yaml'
    with open(sec,'r') as file:
        funds = yaml.full_load(file)
        return funds['funds']
        

    
funds_list = get_funds()   
auth = get_ms_auth_token()

for fund in funds_list:
    snapshot = get_ms_fund_data(auth[0],auth[1],fund)
    print ('P' 
            + " " 
            + parse(snapshot[0]['LastPrice']['Date']).strftime('%Y-%m-%d')
            + " " 
            + str(fund)
            + " " 
            + str(snapshot[0]['LastPrice']['Value']) 
            + " " 
            + (snapshot[0]['LastPrice']['Currency']['Id']))

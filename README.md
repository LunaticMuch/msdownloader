# Introduction

Morningstar Downloader, aka `msdownloader`, is a small script for downloading securities prices from [Morningstar](https://www.morningstar.com) using official APIs rather than doing site scraping and returning the last price in a [hledger](https://hledger.org) suitable price format.

## How it works

The script first places a call to [Morningstar](https://www.morningstar.co.uk) public international website to retrieve an authorization token which is dynamic (i.e. it changes with any call and does not last for more few minutes). The token is then used to call the official Morningstar API for prices and retrieve securitires' prices.
Finally, the script returns a list in the stdin of funds prices following the format requested by hleder with the date equal to the last price date (it is not the date of script execution). 
Example:

```bash
P 2021-01-08 GB00B907VX32 214.18 GBX
P 2021-01-08 GB0006010168 1625.0 GBX
```
## Installation 

Download the script. To install the dependencies run:

```bash
pip install -r requirements.txt
```
## Configuration file

Create a config file, in YAML format, in a location at your choice. The file must contain a key `funds` with a list of ISIN. You can check the included `securities_example.yaml` or the specimen below: 

```yaml
funds:
   - code: GB0006010168
     name: A fund
   - code: GB00B907VX32
     universe: FOGBR$$ALL
     name: Another fund
shares:
  - code: US0258161092
  - code: IT0003497168
```
### Code
The code **must** the ISIN for the security. Unfortunately we cannot accept [WKN](https://en.wikipedia.org/wiki/Wertpapierkennnummer), [VALOR](https://en.wikipedia.org/wiki/Valoren_number), [SEDOL](https://en.wikipedia.org/wiki/SEDOL) or the Morningstar very own identifier. The limitation is in API which cannot accept a list of different type of identifier at the same time. ISIN is definitely the most common.

### Universe
The **universe** is not mandatory. If not added, the universe will be standard one from the UK website whichnormally includes most of securities. In case your security is listed on a *non-default* market, you might need to add the universe. The easiest way to identify the universe is looking at the URL when you are browsing your security. You can either see it as URL parameter, called `UniverseID` or at the end of a parameter called `SecurityToken`, example:
```url
https://tools.morningstar.co.uk/uk/cefreport/default.aspx?SecurityToken=E0GBR00VWL]2]0]FCGBR$$ALL
```

The universe is the last 10 chars, i.e. **FCGBR$$ALL**. They follow a naming convention like the first five chars identify the type of investment and the country (Closed Fund Great Britain) and then a subset ($$ALL). Finding it should be straightforward, if not file a an issue and report the URL.
Universes are not normally required, nor accepted now, for shares.

### Name
The name is reserved for future use. The idea is to print a custom name in the output instead forcing the usage of ISIN which might not be the identifier you use today.

## Compatibility
Morningstar provides a wide range of a financial instruments. Most of tests are realized on international markets (EMEA and APAC) The script has been found compabile with:
- **funds**: Open Funds, Closed Funds, ETF
- **shares**: stocks traded on most markets
## Usage

Run the file `msdownloader.py` with the following arguments:

|Argument|Accept|Description|
|---|---|---|
|-c|\<path to the YAML file of choice>|File name (with or without the full path) of the YAML config file containing all the securities|
|-d|XH7946842KD| The ISIN code for which a full dump is requested. The script returns the whole JSON payload as returned by the API|
|-l|XH7946842KD| A lookup function similar to the search box on the website. It might produce limited results|
|-x||If specified, it forces the conversion from GBX to GBP|
|-b||Return the beancount format instead of Ledger (Default)|
|-o|output.txt|Save the output to a file instead of using the console|
|-w||Force file overwrite instead of append (default)|
## Limits

The currenct script is tested only against funds (ETC/ETF works as funds).
This script has been tested with Python >3.5 only

## Todo

- [X] Accept arguments from command lines
- [X] Provide conversion for GBX into GBP
- [X] Save output directly into a file
- [X] Save output into different format (ledger, beancount, etc)
- [ ] Test for currencies / shares / other type of securities
- [X] Make a single call for multiple securities at the same time
- [ ] Add the failback support to public API endpoint
- [ ] Improve code quality
- [X] Utilize conversion per security
- [ ] Download currencies
- [ ] Download Bond information
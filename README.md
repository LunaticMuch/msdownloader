# Introduction

Morningstar Downloader, aka `msdownloader`, is a small script for downloading securities prices from [Morningstar](https://www.morningstar.com) using official APIs rather than doing site scraping and returning the last price in a [hledger](https://hledger.org) suitable price format.

## How it works

The script first places a call to [Morningstar](https://www.morningstar.co.uk) public international website to retrieve an authorization token which is dynamic (i.e. it changes with any call and does not last for more few minutes). The token is then used to call the official Morningstar API for prices and retrieve the snapshot for each fund.
Finally, the script returns a list in the stdin of funds prices following the format requested by hleder with the date equal to the last price date (it is not the date of script execution). Example:

```bash
P 2021-01-08 GB00B907VX32 214.18 GBX
P 2021-01-08 GB0006010168 1625.0 GBX
```
## Installation 

Download the script. To install the dependencies run:

```bash
pip install -r requirements.txt
```

Create a config file, in YAML format, in a location at your choice. The file must contain a key `funds` with a list of ISIN. You can check the included `securities_example.yaml` or the specimen below: 

```yaml
funds:
   - GB0006010168
   - GB00B907VX32
```
## Usage

Run the file `msdownloader.py` with the following arguments:

|Argument|Description|
|---|---|
|-c|\<path to the YAML file of choiche>|
|-x|to force the conversion from GBX to GBP|

## Limits

The currenct script is tested only against funds (ETC/ETF works as funds).
This script has been tested with Python >3.5 only

## Todo

- [X] Accept arguments from command lines
- [X] Provide conversion for GBX into GBP
- [ ] Save output directly into a file
- [ ] Save output into different format (ledger, beancount, etc)
- [ ] Test for currencies / shares / other type of securities
- [ ] Make a single call for multiple securities at the same time
- [ ] Add the failback support to public API endpoint
- [ ] Improve code quality
- [ ] Utilize conversion per security
- [ ] Enable usage of Sedol instead of ISIN
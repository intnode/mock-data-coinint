from __future__ import print_function
import os, requests, csv, time, argparse, json
from bs4 import BeautifulSoup
from web3 import Web3
import pandas as pd
from io import StringIO
from tqdm import tqdm
from re import sub
from dotenv import load_dotenv
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

load_dotenv()
CMC_API = os.environ.get('CMC_API')

def snake_case(s):
  return '_'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower()

ses = requests.Session()
retries = Retry(total=10,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504])

ses.mount('http://', HTTPAdapter(max_retries=retries))
headers = {'User-Agent': 'Mozilla/5.0'}
url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?CMC_PRO_API_KEY={CMC_API}&limit=150"
req = ses.get(url)
listing_latest = req.json()
reqdf = pd.DataFrame(listing_latest.get("data"))
reqdf["last_updated"] = pd.to_datetime(reqdf["last_updated"])
reqdf["convert_symbol"] = ["USD"]*len(reqdf)
quote_df = pd.DataFrame({k:v for k,v in reqdf["quote"].apply(lambda x:x.get("USD")).items()}).T
quote_df.drop("last_updated",axis=1,inplace=True)
reqdf = reqdf.join(quote_df)
reqdf["image"] = reqdf["symbol"].apply(lambda x: f"https://raw.githubusercontent.com/alexandrebouttier/coinmarketcap-icons-cryptos/main/icons/{x.casefold()}.png")
reqdf.rename(columns={"id":"coin_id","name":"coin_name","cmc_rank":"rank","price":"current_price","market_cap_dominance":"dominance"},inplace=True)
resdf = reqdf[["coin_id","coin_name","slug","symbol","image","current_price","convert_symbol","circulating_supply","total_supply","max_supply","market_cap","fully_diluted_market_cap",
              "dominance","rank","percent_change_1h","percent_change_24h","percent_change_7d","percent_change_30d","volume_24h","last_updated"]]
slug_sym_dict = {resdf.slug.iloc[i]:resdf.symbol.iloc[i] for i in range(len(reqdf))}
id_sym_dict = {resdf.coin_id.iloc[i]:resdf.symbol.iloc[i] for i in range(len(reqdf))}

url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/info?CMC_PRO_API_KEY={CMC_API}&id="
for coin_id in list(id_sym_dict.keys()):
  url = f"{url}{coin_id},"
url = url[:-1]
req = ses.get(url,headers=headers)
coin_metadata = req.json()

url = f"https://api.coinmarketcap.com/data-api/v3/project-info/detail?CMC_PRO_API_KEY={CMC_API}&slug={slug_sym_dict.keys()}"
req = ses.get(url,headers=headers)
req_json = req.json()['data']
ind_team = []
org_team = []
for tai in req_json.get("data").get("tai").get("teamAdvisorInvestors"):
  if tai.get("type") == "Organization":
    org_team.append({
      "name": "Alameda Research",
      "location": "Hong Kong",
      "foundedYear": "",
      "link": "",
      "logoImg": "https://raw.githubusercontent.com/intnode/mock-data-coinint/master/coin_page/BTC/img/alameda_research.jpg"
    })
  team.append({
    "fullname": name,
    "position": "Bitcoin Core Contributor",
    "image": "https://raw.githubusercontent.com/intnode/mock-data-coinint/master/coin_page/BTC/img/giel_van_schijndel.jpg",
    "description": "",
    "social": {
      "ig": "",
      "fb": "",
      "linkedin": ""
    }
  })
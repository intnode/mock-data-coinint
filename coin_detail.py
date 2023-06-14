import requests, json, os, sys, wget, shutil
import pandas as pd
import numpy as np
from re import sub
from dotenv import load_dotenv
from tqdm import tqdm
from collections import OrderedDict
from tradingnode.simple_gauge import simple_asset_gauge, weighted_asset_gauge, indicator_dict, moving_average_oscillator_weight
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import timedelta
from bs4 import BeautifulSoup

load_dotenv()
CMC_API = os.environ.get('CMC_API')
CC_API = os.environ.get('CC_API')
Glassnode_API = os.environ.get('Glassnode_API')
AV_API = os.environ.get('AV_API')
headers = {'User-Agent': 'Mozilla/5.0'}
CMC2CC = {"AGIX":"AGI"} # Cryptocompare currently use this temporary name

PVM_coingecko_AGG = OrderedDict((
                    ("price","last"),
                    ("volume","last"),
                    ("marketcap","last"),
                    ))

OHLCV_AGG = OrderedDict((
            ('Open', 'first'),
            ('High', 'max'),
            ('Low', 'min'),
            ('Close', 'last'),
            ('Volume', 'sum'),
          ))

if os.path.exists("utils/gecko_coinlist.json"):
  gecko_coinlist = pd.read_json("utils/gecko_coinlist.json")
  pass
else:
  url = "https://api.coingecko.com/api/v3/coins/list"
  req = requests.get(url)
  gecko_coinlist = pd.DataFrame(req.json())
  gecko_coinlist.to_json("utils/gecko_coinlist.json",indent=2,orient="records")

with open("utils/available_assets.json") as f:
  available_assets = json.load(f)

with open("utils/chain_explorer.json") as f:
  chain_explorers = json.load(f)
  chain_explorer_links = {item['chain']: item["explorer"] for item in chain_explorers}

with open("utils/sym2id.json") as f:
  sym2id = json.load(f)
with open("utils/sym2slug.json") as f:
  sym2slug = json.load(f)
with open("utils/sym2name.json") as f:
  sym2name = json.load(f)

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

def snake_case(s):
  return '_'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower()

def generate_coin_details_static():
  try:
    ses = requests.Session()
    retries = Retry(total=10,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504])

    ses.mount('http://', HTTPAdapter(max_retries=retries))
    ses.mount('https://', HTTPAdapter(max_retries=retries))

    url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/info?CMC_PRO_API_KEY={CMC_API}&id="
    for asset in available_assets:
      url = f"{url}{sym2id[asset]},"
    url = url[:-1]
    req = ses.get(url,headers=headers)
    coin_metadata = pd.DataFrame(req.json().get('data')).T
    
    for cmc_metadata in tqdm(coin_metadata.to_dict(orient="records")):
      if not os.path.exists(f"img/coin/{cmc_metadata['slug']}.png"):
        wget.download(cmc_metadata['logo'],f"img/coin/{cmc_metadata['slug']}.png")
      categories, categories_name = [cmc_metadata["category"]], [cmc_metadata["category"].capitalize()]
      if cmc_metadata.get('tags') and cmc_metadata.get('tag-names'):
        for (item_id, item_name) in zip(cmc_metadata['tags'],cmc_metadata['tag-names']):
          if item_id.find("portfolio") == -1:
            categories.append(item_id)
            categories_name.append(item_name)

      cmc_url = f"https://coinmarketcap.com/currencies/{cmc_metadata['slug']}/holders"
      req = ses.get(cmc_url,headers=headers)
      bs = BeautifulSoup(req.text, 'html.parser')
      bs_audits = bs.find_all("div",{"class":"sc-aef7b723-0 cwjwWo mainChainAddress"})
      audits = list(set([str(bs_audit).split(">")[1].split("<")[0] for bs_audit in bs_audits]))

      metadata = {
        "id": cmc_metadata["id"],
        "slug": cmc_metadata["slug"],
        "fullname": cmc_metadata["name"],
        "symbol": cmc_metadata["symbol"],
        "icon": f"https://raw.githubusercontent.com/intnode/mock-data-coinint/master/img/coin/{cmc_metadata['slug']}",
        "categories": categories,
        "categories_name" : categories_name
      }
      contracts = []
      for contract in cmc_metadata["contract_address"]:
        contracts.append({
          "chain": contract["platform"]["name"],
          "address": contract["contract_address"],
          "link": f"{chain_explorer_links[contract['platform']['name']]}token/{contract['contract_address']}" if contract["platform"]["name"] in chain_explorer_links.keys() else None
        })
      token_links = {
        "website": cmc_metadata["urls"]["website"],
        "explorer": cmc_metadata["urls"]["explorer"],
        "wallets": ["metamask"], # Auto assign metamask in this version
        "community":{
          "twitter": cmc_metadata["urls"]["twitter"][0] if len(cmc_metadata["urls"]["twitter"]) != 0 else None,
          "discord": None, # There is no info of discord in this version
          "reddit": cmc_metadata["urls"]["reddit"][0] if len(cmc_metadata["urls"]["reddit"]) != 0 else None,
          "facebook": cmc_metadata["urls"]["facebook"][0] if len(cmc_metadata["urls"]["facebook"]) != 0 else None,
        },
        "source_code": cmc_metadata["urls"]["source_code"][0] if len(cmc_metadata["urls"]["source_code"]) != 0 else None,
        "audit": audits,
        "contracts": contracts
      }
      
      if not os.path.exists(f"coin_page/{metadata['symbol']}/what_is.json"):
        with open(f"coin_page/{cmc_metadata['symbol']}/what_is.json","w") as f:
          json.dump([],f)
      if not os.path.exists(f"coin_page/{metadata['symbol']}/roadmap.json"):
        with open(f"coin_page/{cmc_metadata['symbol']}/roadmap.json","w") as f:
          json.dump([],f)
      
      with open(f"coin_page/{metadata['symbol']}/market_data.json") as f:
        market_data = json.load(f)[0]

      project_info_url = f"https://api.coinmarketcap.com/data-api/v3/project-info/detail?slug={metadata['slug']}"
      project_info_req = ses.get(project_info_url)
      project_info = project_info_req.json().get('data')
      team_, investors_ = [], []
      team, investors = [], []
      if project_info.get("tai"):
        teamAdvisorInvestors = project_info.get("tai").get("teamAdvisorInvestors")
        for tai in teamAdvisorInvestors:
          if not os.path.exists(f"img/avatar/{snake_case(tai['name'])}.png") and tai.get("avatar"):
            r = requests.get(tai['avatar'], stream=True, headers=headers)
            with open(f"img/avatar/{snake_case(tai['name'])}.png", 'wb') as f:
              r.raw.decode_content = True
              shutil.copyfileobj(r.raw, f)
          
          if tai["identityType"] == 0:
            team_.append({
              "fullname": tai["name"],
              "position": tai["jobTitle"] if tai.get("jobTitle") else "",
              "location": tai["location"] if tai.get("location") else "",
              "foundedYear": str(tai["foundationTime"]) if tai.get("foundationTime") else "",
              "image": f"https://raw.githubusercontent.com/intnode/mock-data-coinint/master/img/avatar/{snake_case(tai['name'])}.png" if tai.get("avatar") else f"https://raw.githubusercontent.com/intnode/mock-data-coinint/master/img/avatar/Unknown_person.jpg",
              "description": "",
              "urls": {
                "link": "",
                "ig": "",
                "fb": "",
                "linkedin": ""
                }
              })
          
            if tai["type"] == "Individual":
              team.append({
                "fullname": tai["name"],
                "position": tai["jobTitle"] if tai.get("jobTitle") else "",
                "image": f"https://raw.githubusercontent.com/intnode/mock-data-coinint/master/img/avatar/{snake_case(tai['name'])}.png" if tai.get("avatar") else f"https://raw.githubusercontent.com/intnode/mock-data-coinint/master/img/avatar/Unknown_person.jpg",
                "description": "",
                "social": {
                  "ig": "",
                  "fb": "",
                  "linkedin": ""
                  }
                })
              
          elif tai["identityType"] == 1:
            investors_.append({
              "fullname": tai["name"],
              "position": tai["jobTitle"] if tai.get("jobTitle") else "",
              "location": tai["location"] if tai.get("location") else "",
              "foundedYear": str(tai["foundationTime"]) if tai.get("foundationTime") else "",
              "image": f"https://raw.githubusercontent.com/intnode/mock-data-coinint/master/img/avatar/{snake_case(tai['name'])}.png" if tai.get("avatar") else f"https://raw.githubusercontent.com/intnode/mock-data-coinint/master/img/avatar/Unknown_person.jpg",
              "description": "",
              "urls": {
                "link": "",
                "ig": "",
                "fb": "",
                "linkedin": ""
                }
              })
          
            if tai["type"] == "Organization":
              investors.append({
                "name": tai["name"],
                "location": tai["location"] if tai.get("location") else "",
                "foundedYear": str(tai["foundationTime"]) if tai.get("foundationTime") else "",
                "link": "",
                "logoImg": f"https://raw.githubusercontent.com/intnode/mock-data-coinint/master/img/avatar/{snake_case(tai['name'])}.png" if tai.get("avatar") else f"https://raw.githubusercontent.com/intnode/mock-data-coinint/master/img/avatar/Unknown_person.jpg",
                })
      
      token_distributions = []
      if project_info.get("trs"):
        distributions = project_info.get("trs").get("distributions")
        for items in distributions:
          token_distributions.append({
            "name": items["holder"],
            "percentage": items["percentage"],
            "value": market_data["total_supply"]*items["percentage"] if market_data["total_supply"] != None else None
          })
      else:
        token_distributions.append({
          "name": metadata["symbol"],
          "percentage": 100,
          "value": market_data["total_supply"]*100 if market_data["total_supply"] != None else None
        })  

      with open(f"coin_page/{metadata['symbol']}/investor.json","w") as f:
        json.dump(investors, f, indent=2)
      with open(f"coin_page/{metadata['symbol']}/investor_.json","w") as f:
        json.dump(investors_, f, indent=2)
      with open(f"coin_page/{metadata['symbol']}/team.json","w") as f:
        json.dump(team, f, indent=2)
      with open(f"coin_page/{metadata['symbol']}/team_.json","w") as f:
        json.dump(team_, f, indent=2)
      with open(f"coin_page/{metadata['symbol']}/token_distribution.json","w") as f:
        json.dump(token_distributions, f, indent=2)
      with open(f"coin_page/{metadata['symbol']}/metadata.json","w") as f:
        json.dump(metadata, f, indent=2)
      with open(f"coin_page/{metadata['symbol']}/token_links.json","w") as f:
        json.dump(token_links, f, indent=2)

  except Exception as e:
    print(e)

# holder_url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/holders/count?id=7083&range=7d"
# holder_req = requests.get(holder_url,headers=headers)
# total_holders = pd.Series(holder_req.json().get('data').get('points')).iloc[-1]
# ratio_url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/holders/ratio?id=7083&range=7d"
# ratio_req = requests.get(ratio_url,headers=headers)
# holder_ratio = pd.Series(ratio_req.json().get('data').get('points')).iloc[-1]

def generate_coin_details_dynamic():
  ses = requests.Session()
  retries = Retry(total=10,
                  backoff_factor=1,
                  status_forcelist=[429, 500, 502, 503, 504])

  ses.mount('http://', HTTPAdapter(max_retries=retries))
  ses.mount('https://', HTTPAdapter(max_retries=retries))

  if os.path.exists("utils/cryptocompare_blockchain_asset_list.json"):
    cryptocompare_blockchain_asset_list = pd.read_json("utils/cryptocompare_blockchain_asset_list.json")
  else:
    url = f"https://min-api.cryptocompare.com/data/blockchain/list?api_key={CC_API}"
    req = requests.get(url)
    cryptocompare_blockchain_asset_list = pd.DataFrame(req.json().get("Data")).T
    cryptocompare_blockchain_asset_list.to_json("utils/cryptocompare_blockchain_asset_list.json",indent=2,orient="records")

  if os.path.exists("utils/glassnode_asset_list.json"):
    glassnode_asset_list = pd.read_json("utils/glassnode_asset_list.json")
  else:
    url = f"https://api.glassnode.com/v1/metrics/assets"
    params = {'api_key': Glassnode_API, 'f':'JSON'}
    req = ses.get(url, params=params)
    glassnode_asset_list = pd.DataFrame(req.json())
    glassnode_asset_list.to_json("utils/glassnode_asset_list.json",indent=2,orient="records")

  if os.path.exists("utils/gecko_coinlist.json"):
    gecko_coinlist = pd.read_json("utils/gecko_coinlist.json")
  else:
    url = "https://api.coingecko.com/api/v3/coins/list"
    req = ses.get(url)
    gecko_coinlist = pd.DataFrame(req.json())
    gecko_coinlist.to_json("utils/gecko_coinlist.json",indent=2,orient="records")
      
  for asset in tqdm(available_assets):

    if asset in CMC2CC:
      asset_cc = CMC2CC[asset]
    else:
      asset_cc = asset
    
    if asset_cc in cryptocompare_blockchain_asset_list.symbol.tolist():
      cc_blockchain_url = f"https://min-api.cryptocompare.com/data/blockchain/histo/day?fsym={asset_cc}&limit=2000&api_key={CC_API}"
      req = ses.get(cc_blockchain_url)
      cc_key_metric = pd.DataFrame(req.json().get("Data").get("Data"))
      cc_key_metric.index = pd.to_datetime(cc_key_metric.time,unit="s")
      cc_key_metric.drop(["id","symbol","current_supply","time"],axis=1,inplace = True)
      cc_key_metric["token_holder"] = cc_key_metric.unique_addresses_all_time-cc_key_metric.zero_balance_addresses_all_time
    else:
      cc_key_metric = pd.DataFrame([])

    if asset in glassnode_asset_list.symbol.tolist():
      params = {'a': asset, 'i': "24h", 'api_key': Glassnode_API, 'f':'JSON'}
      if asset_cc in cryptocompare_blockchain_asset_list.symbol.tolist():
        metric_dict = {
                      "transaction_fee":"https://api.glassnode.com/v1/metrics/fees/volume_sum",
                      "miner_revenue":"https://api.glassnode.com/v1/metrics/mining/revenue_sum",
                      "percent_balance_on_exchanges":"https://api.glassnode.com/v1/metrics/distribution/balance_exchanges_relative",
                      "exchange_withdrawals":"https://api.glassnode.com/v1/metrics/transactions/transfers_from_exchanges_count",
                      "exchange_deposits":"https://api.glassnode.com/v1/metrics/transactions/transfers_to_exchanges_count",
                      }
      else:
        metric_dict = {
                      "transactions_count":"https://api.glassnode.com/v1/metrics/transactions/count",
                      "active_address":"https://api.glassnode.com/v1/metrics/addresses/active_count",
                      "token_holder":"https://api.glassnode.com/v1/metrics/addresses/non_zero_count",
                      "transaction_fee":"https://api.glassnode.com/v1/metrics/fees/volume_sum",
                      "miner_revenue":"https://api.glassnode.com/v1/metrics/mining/revenue_sum",
                      "percent_balance_on_exchanges":"https://api.glassnode.com/v1/metrics/distribution/balance_exchanges_relative",
                      "exchange_withdrawals":"https://api.glassnode.com/v1/metrics/transactions/transfers_from_exchanges_count",
                      "exchange_deposits":"https://api.glassnode.com/v1/metrics/transactions/transfers_to_exchanges_count",
                      }

      gn_key_metric_list = []
      for key, url in metric_dict.items():
        req = ses.get(url, params=params)
        try:
          read_df = pd.DataFrame(json.loads(req.text)).set_index('t') # Avoid big values
          read_df.index = pd.to_datetime(read_df.index,unit="s")
          read_df.columns = [key]
          gn_key_metric_list.append(read_df)
        except:
          pass

      gn_key_metric = pd.concat(gn_key_metric_list,axis=1).dropna()
    else:
      gn_key_metric = pd.DataFrame([])

    ## Coin gecko market chart have 3 values, price, market_cap and 24hr volume ##

    for asset in available_assets:
      filter_by_symbol = gecko_coinlist[gecko_coinlist.symbol==asset.casefold()]
      if len(filter_by_symbol)==1:
        gecko_id = filter_by_symbol.id.values[0]
      else:
        filter_by_symbol_name = filter_by_symbol[filter_by_symbol.name==sym2name[asset]]
        filter_by_symbol_slug = filter_by_symbol[filter_by_symbol.id==sym2slug[asset]]
        if len(filter_by_symbol_name) ==1:
          gecko_id = filter_by_symbol_name.id.values[0]
        elif len(filter_by_symbol_slug) ==1:
          gecko_id = filter_by_symbol_slug.id.values[0]
        else:
          filter_by_symbol_contains_name = filter_by_symbol[filter_by_symbol.name.str.find(sym2name[asset])!=-1]
          if len(filter_by_symbol_contains_name) == 1:
            gecko_id = filter_by_symbol_contains_name.id.values[0]
          else:
            raise ValueError(f"Not found matching symbol between cmc and cg for {asset}")
    
    # # Get Hourly data
    url = f"https://api.coingecko.com/api/v3/coins/{gecko_id}/market_chart?vs_currency=usd&days=90"
    req = ses.get(url)
    price1h = pd.DataFrame(req.json().get("prices"),columns=["time","price"]).set_index('time').iloc[:-1]
    marketcap1h = pd.DataFrame(req.json().get("total_volumes"),columns=["time","volume"]).set_index('time').iloc[:-1]
    volumnes1h = pd.DataFrame(req.json().get("market_caps"),columns=["time","marketcap"]).set_index('time').iloc[:-1]
    pvm1h = pd.concat([price1h,volumnes1h,marketcap1h],axis=1)
    pvm1h.index = pd.Series(pd.to_datetime(pvm1h.index, unit="ms")).apply(lambda x: hour_rounder(x)- timedelta(hours=1))
    pvm1h = pvm1h.resample("1h",closed="left",label="left").agg(PVM_coingecko_AGG)
    pvm3h = pvm1h.resample("3h",closed="left",label="left").agg(PVM_coingecko_AGG)
    pvm1h["time"] = pvm1h.index
    pvm3h["time"] = pvm3h.index
    pvm1h.iloc[-24*7:].to_json(f"coin_page/{asset}/price_chart_7d.json",orient="records",indent=2)
    pvm1h.iloc[-24*30:].to_json(f"coin_page/{asset}/price_chart_1m.json",orient="records",indent=2)
    pvm3h.to_json(f"coin_page/{asset}/price_chart_3m.json",orient="records",indent=2)
    
    # Get Daily data
    url = f"https://api.coingecko.com/api/v3/coins/{gecko_id}/market_chart?vs_currency=usd&days=max"
    req = ses.get(url)

    price1d = pd.DataFrame(req.json().get("prices"),columns=["time","price"]).set_index('time').iloc[:-1]
    marketcap1d = pd.DataFrame(req.json().get("total_volumes"),columns=["time","volume"]).set_index('time').iloc[:-1]
    volumnes1d = pd.DataFrame(req.json().get("market_caps"),columns=["time","marketcap"]).set_index('time').iloc[:-1]
    pvm1d = pd.concat([price1d,volumnes1d,marketcap1d],axis=1)
    pvm1d.index = pd.Series(pd.to_datetime(pvm1d.index, unit="ms")).apply(lambda x: x - timedelta(days=1)) #coingecko provide end time instead of start time
    pvm1d = pvm1d.resample("1d",closed="left",label="left").agg(PVM_coingecko_AGG)
    pvm1w = pvm1d.resample("W-MON",closed="left",label="left").agg(PVM_coingecko_AGG)
    pvm1d.iloc[-365:].to_json(f"coin_page/{asset}/price_chart_1y.json",orient="records",indent=2)
    pvm1w.to_json(f"coin_page/{asset}/price_chart_all.json",orient="records",indent=2)

    key_metric = pd.concat([pvm1d,cc_key_metric,gn_key_metric],axis=1).dropna()
    key_metric['time'] = key_metric.index
    key_metric.to_json(f"coin_page/{asset}/key_metric_all.json",orient="records",indent=2)
    key_metric.iloc[-365:].to_json(f"coin_page/{asset}/key_metric_1y.json",orient="records",indent=2)
    key_metric.iloc[-90:].to_json(f"coin_page/{asset}/key_metric_3m.json",orient="records",indent=2)
    key_metric.iloc[-30:].to_json(f"coin_page/{asset}/key_metric_1m.json",orient="records",indent=2)
    key_metric.iloc[-7:].to_json(f"coin_page/{asset}/key_metric_7d.json",orient="records",indent=2)

    ohlcv = pd.read_json(f"OHLCV_1h/{asset}_1h.json").set_index("time")
    ohlcv.index = pd.to_datetime(ohlcv.index, unit="s")
    ohlcv.columns = ohlcv.columns.str.capitalize()
    trend_analysis = {}
    for resolution in ["1H","4H","1D","1W-MON"]:
      try:
        gauge_str, gauge_val, signal_dict = weighted_asset_gauge(ohlcv.resample(resolution,closed="left",label="left").agg(OHLCV_AGG).iloc[-1000:], indicator_dict, moving_average_oscillator_weight)
        trend_analysis[resolution.split("-")[0].casefold()] = {
                                                    "value": gauge_val,
                                                    "analysis": gauge_str
                                                    }
      except: # In case of some resolution not have enough data
        trend_analysis[resolution.split("-")[0].casefold()] = {
                                            "value": None,
                                            "analysis": ''
                                            }

    with open(f"coin_page/{asset}/technical_analysis.json", "w") as f:
      json.dump(trend_analysis,f,indent=2)

  general_news_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topic=blockchain&apikey={AV_API}"
  req = ses.get(general_news_url)
  general_blockchain_news = pd.DataFrame(req.json().get("feed"))
  general_blockchain_news.time_published = pd.to_datetime(general_blockchain_news.time_published)

  for asset in tqdm(available_assets):
    news_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=CRYPTO:{asset}&apikey={AV_API}"
    req = ses.get(news_url)
    news_df = pd.DataFrame(req.json().get("feed"))
    if len(news_df) != 0:
      news_df.time_published = pd.to_datetime(news_df.time_published)
      news_df.to_json(f"coin_page/{asset}/news_feed.json",orient="records",indent=2)
    else:
      general_blockchain_news.to_json(f"coin_page/{asset}/news_feed.json",orient="records",indent=2)

  print("Update coin detail page complete")
    
if __name__ == "__main__":
  generate_coin_details_dynamic()
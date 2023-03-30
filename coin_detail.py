import requests, json, os, sys
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from tqdm import tqdm
from collections import OrderedDict
from tradingnode.simple_gauge import simple_asset_gauge, weighted_asset_gauge, indicator_dict, moving_average_oscillator_weight

load_dotenv()
CMC_API = os.environ.get('CMC_API')
CC_API = os.environ.get('CC_API')
Glassnode_API = os.environ.get('Glassnode_API')
AV_API = os.environ.get('AV_API')

PVM_AGG = OrderedDict((
           ("price","last"),
           ("volume","sum"),
           ("marketcap","last"),
           ("time","last"),
          ))

OHLCV_AGG = OrderedDict((
            ('Open', 'first'),
            ('High', 'max'),
            ('Low', 'min'),
            ('Close', 'last'),
            ('Volume', 'sum'),
          ))

slug_to_symbol = {"bitcoin":"BTC", "ethereum":"ETH", "uniswap":"UNI", "aave":"AAVE", "tether":"USDT"}

def generate_coin_details(asset_list):
  for asset in tqdm(asset_list):
    if not os.path.exists(f"coin_page/{asset}"):
      os.mkdir(f"coin_page/{asset}")
    url = f"https://api.glassnode.com/v1/metrics/market/marketcap_usd"
    params = {'a': slug_to_symbol[asset], 'i': "1h", 'api_key': Glassnode_API, 'f':'JSON'}
    req = requests.get(url, params=params)
    read_m = pd.read_json(req.text, convert_dates=['t']).set_index('t')
    read_m.columns = ['marketcap']
    url = f"https://api.glassnode.com/v1/metrics/market/price_usd_ohlc"
    read_v = pd.read_json(requests.get("https://api.glassnode.com/v1/metrics/transactions/transfers_volume_sum",params=params).text, convert_dates=['t']).set_index('t')
    read_v.columns = ['volume']
    read_c = pd.read_json(requests.get("https://api.glassnode.com/v1/metrics/market/price_usd_close",params=params).text,convert_dates='t').set_index('t')
    read_c.columns = ['price']
    price = pd.concat([read_c,read_v,read_m],axis=1).dropna(axis=0)
    price['time'] = price.index
    price.iloc[-24*7:].to_json(f"coin_page/{asset}/price_chart_7d.json",orient="records")
    price.iloc[-24*30:].to_json(f"coin_page/{asset}/price_chart_1m.json",orient="records")
    price.resample("3h").agg(PVM_AGG).iloc[-8*90:].to_json(f"coin_page/{asset}/price_chart_3m.json",orient="records")
    price.resample("1d").agg(PVM_AGG).iloc[-365:].to_json(f"coin_page/{asset}/price_chart_1y.json",orient="records")
    price.resample("W-MON").agg(PVM_AGG).to_json(f"coin_page/{asset}/price_chart_all.json",orient="records")

    read_v.columns = ['Volume']
    read_ohlc = pd.read_json(requests.get("https://api.glassnode.com/v1/metrics/market/price_usd_ohlc",params=params).text,convert_dates='t').set_index('t')
    ohlc_df = pd.DataFrame([[data['o'],data['h'],data['l'],data['c']] for data in read_ohlc['o'].values],columns=['Open','High','Low','Close'],index=read_ohlc.index)
    ohlcv = pd.concat([ohlc_df,read_v],axis=1).dropna()
    ohlcv['time'] = ohlcv.index

    trend_analysis = {}
    for resolution in ["1H","4H","1D","1W-MON"]:
      gauge_str, gauge_val, signal_dict = weighted_asset_gauge(ohlcv.resample(resolution).agg(OHLCV_AGG).iloc[-1000:], indicator_dict, moving_average_oscillator_weight)
      trend_analysis[resolution.split("-")[0].casefold()] = {
                                                  "value": gauge_val,
                                                  "analysis": gauge_str
                                                  }

    with open(f"coin_page/{asset}/technical_analysis.json", "w") as f:
      json.dump(trend_analysis,f)

    ohlcv.to_json(f"coin_page/{asset}/OHLCV.json",orient="records")

    params = {'a': slug_to_symbol[asset], 'i': "24h", 'api_key': Glassnode_API, 'f':'JSON'}
    metric_dict = {"price":"https://api.glassnode.com/v1/metrics/market/price_usd_close",
                  "volume": "https://api.glassnode.com/v1/metrics/transactions/transfers_volume_sum",
                  "marketcap": "https://api.glassnode.com/v1/metrics/market/marketcap_usd",
                  "transactions_count":"https://api.glassnode.com/v1/metrics/transactions/count",
                  "active_address":"https://api.glassnode.com/v1/metrics/addresses/active_count",
                  "token_holder":"https://api.glassnode.com/v1/metrics/addresses/non_zero_count",
                  "transaction_fee":"https://api.glassnode.com/v1/metrics/fees/volume_sum",
                  "circulating_supply":"https://api.glassnode.com/v1/metrics/supply/current",
                  "mining_difficulty":"https://api.glassnode.com/v1/metrics/mining/difficulty_latest",
                  "miner_revenue":"https://api.glassnode.com/v1/metrics/mining/revenue_sum",
                  "percent_balance_on_exchanges":"https://api.glassnode.com/v1/metrics/distribution/balance_exchanges_relative",
                  "exchange_withdrawals":"https://api.glassnode.com/v1/metrics/transactions/transfers_from_exchanges_count",
                  "exchange_deposits":"https://api.glassnode.com/v1/metrics/transactions/transfers_to_exchanges_count",
                  }

    key_metric_df_list = []
    for key, url in metric_dict.items():
      req = requests.get(url, params=params)
      try:
        read_df = pd.DataFrame(json.loads(req.text)).set_index('t') # Avoid big values
        read_df.index = pd.to_datetime(read_df.index,unit="s")
        read_df.columns = [key]
        key_metric_df_list.append(read_df)
      except:
        pass

    key_metric_df = pd.concat(key_metric_df_list,axis=1).dropna()
    key_metric_df['time'] = key_metric_df.index
    key_metric_df.to_json(f"coin_page/{asset}/key_metric_all.json",orient="records")
    key_metric_df.iloc[-365:].to_json(f"coin_page/{asset}/key_metric_1y.json",orient="records")
    key_metric_df.iloc[-90:].to_json(f"coin_page/{asset}/key_metric_3m.json",orient="records")
    key_metric_df.iloc[-30:].to_json(f"coin_page/{asset}/key_metric_1m.json",orient="records")
    key_metric_df.iloc[-7:].to_json(f"coin_page/{asset}/key_metric_7d.json",orient="records")

    news_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=CRYPTO:{slug_to_symbol[asset]}&apikey={AV_API}"
    req = requests.get(news_url)
    news_df = pd.DataFrame(req.json().get("feed"))
    news_df.time_published = pd.to_datetime(news_df.time_published)
    news_df.to_json(f"coin_page/{asset}/news_feed.json",orient="records")

  market_data = pd.read_json(f"coin_page/{asset}/market_data.json")
  if os.path.exists(f"coin_page/{asset}/token_distribution.json"):
    token_dist = pd.read_json(f"coin_page/{asset}/token_distribution.json")
    token_dist['value'] = market_data['market_cap'].values*token_dist['percent']
    token_dist.to_json(f"coin_page/{asset}/token_distribution.json",orient="records")
    
if __name__ == "__main__":
  asset_list = ["bitcoin", "ethereum", "uniswap", "aave", "tether"]
  generate_coin_details(asset_list)
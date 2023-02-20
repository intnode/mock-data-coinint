import requests, json, os, sys
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
CMC_API = os.environ.get('CMC_API')
CC_API = os.environ.get('CC_API')

url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?CMC_PRO_API_KEY={CMC_API}&limit=1000"
req = requests.get(url)
listing_latest = req.json()
reqdf = pd.DataFrame(listing_latest.get("data"))
reqdf["last_updated"] = pd.to_datetime(reqdf["last_updated"])
reqdf["convert_symbol"] = ["USD"]*len(reqdf)
quote_df = pd.DataFrame({k:v for k,v in reqdf["quote"].apply(lambda x:x.get("USD")).items()}).T
quote_df.drop("last_updated",axis=1,inplace=True)
reqdf = reqdf.join(quote_df)
reqdf["image"] = reqdf["symbol"].apply(lambda x: f"icons/{x.casefold()}.png")
reqdf.rename(columns={"id":"coin_id","name":"coin_name","cmc_rank":"rank","price":"current_price","market_cap_dominance":"dominance"},inplace=True)
resdf = reqdf[["coin_id","coin_name","symbol","image","current_price","convert_symbol","circulating_supply","total_supply","max_supply","market_cap","fully_diluted_market_cap",
               "dominance","rank","percent_change_1h","percent_change_24h","percent_change_7d","percent_change_30d","volume_24h","last_updated"]]

resdf.to_json("coin_ranking_table.json",orient="records")

num_trending_coins = 30

for top in [100,500]:
  for timeframe in ["1h","24h","7d","30d"]:
    losers = resdf.iloc[:top].sort_values(f"percent_change_{timeframe}",ascending=True).iloc[:num_trending_coins].to_json(orient="records")
    gainers = resdf.iloc[:top].sort_values(f"percent_change_{timeframe}",ascending=False).iloc[:num_trending_coins].to_json(orient="records")
    res = {"resolution":timeframe,
          "top_coin_rank":top,
          "gainers":json.loads(gainers),
          "losers":json.loads(losers)}
    with open(f"gainers_losers_{timeframe}_top{top}.json", "w") as f:
      json.dump(res,f)
  
cmc_trending_coins = ["BTC","ETH","MATIC","SOL","DOT","NEAR","LUNC","SHIB","CAKE","BNB"]
trending_symbol = resdf[resdf.symbol.isin(cmc_trending_coins)]["symbol"].to_list()
left_symbol = list(set(resdf.symbol.to_list()) - set(trending_symbol))

for timeframe in ["24h","7d","30d"]:
  random_trend = list(np.random.choice(left_symbol,num_trending_coins-len(trending_symbol)))
  all_trend = trending_symbol + random_trend
  np.random.shuffle(all_trend)
  trending_df = pd.concat([resdf[resdf.symbol == symbol] for symbol in all_trend])
  trending_df["trending_rank"] = np.arange(1,num_trending_coins+1)
  trending_df.to_json(f"trending_{timeframe}.json",orient="records")

url = f"https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest?CMC_PRO_API_KEY={CMC_API}"
req = requests.get(url)
global_latest = req.json()
reqdf = pd.DataFrame(global_latest.get("data"))
reqdf["last_updated"] = pd.to_datetime(reqdf["last_updated"])
reqdf["convert_symbol"] = ["USD"]*len(reqdf)
quote_df = pd.DataFrame(reqdf.at["USD","quote"],index=['USD'])
quote_df.drop("last_updated",axis=1,inplace=True)
reqdf = reqdf.join(quote_df,rsuffix="_USD")
reqdf = reqdf.drop(reqdf.columns[reqdf.columns.str[-4:] == '_USD'],axis=1)
reqdf = reqdf.drop("quote",axis=1)
market_metric = {"global_metric":json.loads(reqdf.to_json(orient="records"))}
market_metric["market_overview"] = {"market_cryptocurrencies":len(resdf),
                                    "rise":len(resdf.query("percent_change_24h > 0.2")),
                                    "stable":len(resdf.query("abs(percent_change_24h) <= 0.2")),
                                    "fall":len(resdf.query("percent_change_24h < -0.2"))}
with open(f"market_overview.json", "w") as f:
  json.dump(market_metric,f)

top100cc = resdf.iloc[:100].copy()
top100cc.to_json("Top100_coin_ranking_table.json",orient="records")

for symbol in tqdm(top100cc.symbol.to_list()):
  if not os.path.exists(f"OHLCV_1d/{symbol}_1d.json"):
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={symbol}&tsym=USD&allData=true&api_key={CC_API}"
    res = requests.get(url)
    try:
      price_df = pd.DataFrame(res.json().get("Data").get("Data"))[["time","open","high","close","low","volumeto"]]
      price_df.rename(columns={"volumeto":"volume"},inplace=True)
      price_df = price_df.query("(close > 0) and (open > 0) and (high > 0) and (low > 0)")
    except:
      print(f"missing ohlcv of {symbol}")
      price_df = pd.DataFrame([[np.nan]*6],columns=["time","open","high","close","low","volume"])
    price_df.to_json(f"OHLCV_1d/{symbol}_1d.json",orient="records")

for symbol in tqdm(top100cc.symbol.to_list()):
  if not os.path.exists(f"OHLCV_1h/{symbol}_1d.json"):
    url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={symbol}&tsym=USD&limit=2000&api_key={CC_API}"
    res = requests.get(url)
    try:
      price_df = pd.DataFrame(res.json().get("Data").get("Data"))[["time","open","high","close","low","volumeto"]]
      price_df.rename(columns={"volumeto":"volume"},inplace=True)
      price_df = price_df.query("(close > 0) and (open > 0) and (high > 0) and (low > 0)")
    except:
      print(f"missing ohlcv of {symbol}")
      price_df = pd.DataFrame([[np.nan]*6],columns=["time","open","high","close","low","volume"])
    price_df.to_json(f"OHLCV_1h/{symbol}_1h.json",orient="records")

for symbol in tqdm(top100cc.symbol.to_list()):
  price_df = pd.read_json(f"OHLCV_1h/{symbol}_1h.json")
  price_df = price_df[["time","close"]]
  price_df.iloc[-(24*7):].to_json(f"Price7d/{symbol}.json",orient="records")



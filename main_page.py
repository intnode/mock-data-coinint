import requests, json, os, sys, glob
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

load_dotenv()
CMC_API = os.environ.get('CMC_API')
CC_API = os.environ.get('CC_API')

def generate_main_page():
  try:
    ses = requests.Session()
    retries = Retry(total=10,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504])

    ses.mount('http://', HTTPAdapter(max_retries=retries))

    if not os.path.exists("main_page"):
      os.mkdir("main_page")
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?CMC_PRO_API_KEY={CMC_API}&limit=1000"
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
    resdf = reqdf[["coin_id","coin_name","symbol","slug","image","current_price","convert_symbol","circulating_supply","total_supply","max_supply","market_cap","fully_diluted_market_cap",
                  "dominance","rank","percent_change_1h","percent_change_24h","percent_change_7d","percent_change_30d","volume_24h","volume_change_24h","last_updated"]]
    resdf.to_json(f"main_page/coin_ranking_table.json",orient="records",indent=2)
    
    sym2slug = {resdf.symbol.iloc[i]:resdf.slug.iloc[i] for i in range(len(resdf))}
    sym2name = {resdf.symbol.iloc[i]:resdf.coin_name.iloc[i] for i in range(len(resdf))}
    sym2id = {resdf.symbol.iloc[i]:int(resdf.coin_id.iloc[i]) for i in range(len(resdf))}
    slug2id = {resdf.slug.iloc[i]:int(resdf.coin_id.iloc[i]) for i in range(len(resdf))}

    
    if os.path.exists("utils/sym2slug.json"):
      with open("utils/sym2slug.json", "r") as f:
        existed_sym2slug = json.load(f)
    else:
      existed_sym2slug = {}
    if os.path.exists("utils/sym2id.json"):
      with open("utils/sym2id.json", "r") as f:
        existed_sym2id = json.load(f)
    else:
      existed_sym2id = {}
    if os.path.exists("utils/slug2id.json"):
      with open("utils/slug2id.json", "r") as f:
        existed_slug2id = json.load(f)
    else:
      existed_slug2id = {}
    if os.path.exists("utils/sym2name.json"):
      with open("utils/sym2name.json", "r") as f:
        existed_sym2name = json.load(f)
    else:
      existed_sym2name = {}
    
    sym2slug.update(existed_sym2slug)
    sym2id.update(existed_sym2id)
    slug2id.update(existed_slug2id)
    sym2name.update(existed_sym2name)
    
    with open("utils/sym2slug.json", "w") as f:
      json.dump(sym2slug, f, indent=2)
    with open("utils/sym2id.json", "w") as f:
      json.dump(sym2id, f, indent=2)
    with open("utils/slug2id.json", "w") as f:
      json.dump(slug2id, f, indent=2)
    with open("utils/sym2name.json", "w") as f:
      json.dump(sym2name, f, indent=2)

    num_coins = 150

    for top in [25,50,100,500]:
      for timeframe in ["1h","24h","7d","30d"]:
        losers = resdf.iloc[:top].sort_values(f"percent_change_{timeframe}",ascending=True).iloc[:num_trending_coins].to_json(orient="records")
        gainers = resdf.iloc[:top].sort_values(f"percent_change_{timeframe}",ascending=False).iloc[:num_trending_coins].to_json(orient="records")
        res = {"resolution":timeframe,
              "top_coin_rank":top,
              "gainers":json.loads(gainers),
              "losers":json.loads(losers)}
        with open(f"main_page/gainers_losers_{timeframe}_top{top}.json", "w") as f:
          json.dump(res,f,indent=2)
      
    top_cc = resdf.iloc[:num_coins].copy()
    ## In this phase, we will use top volume_change_24h*abs(percent_change_{x}h) of top 150 coin as trending coin in {x} timeframe"
    for timeframe in ["24h","7d","30d"]:
      trending_indicator = top_cc.volume_change_24h*np.abs(top_cc[f"percent_change_{timeframe}"])
      trending_df = top_cc.iloc[trending_indicator.sort_values(ascending=False).index].copy()
      trending_df["trending_rank"] = np.arange(1,num_trending_coins+1)
      trending_df.to_json(f"main_page/trending_{timeframe}.json",orient="records",indent=2)

    url = f"https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest?CMC_PRO_API_KEY={CMC_API}"
    req = ses.get(url)
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
    with open(f"main_page/market_overview.json", "w") as f:
      json.dump(market_metric,f,indent=2)
      
    ##############################################
    ## We not need to use OHLCV1d at this version ##
    ##############################################
  
    # if not os.path.exists("OHLCV_1d"):
    #   os.mkdir("OHLCV_1d")    
    # if os.path.exists(f"main_page/available_OHLCV.json"):
    #   available_OHLCV = list(pd.read_json(f"main_page/available_OHLCV.json").to_numpy().flatten())
    # else:
    #   available_OHLCV = []
    # for symbol in tqdm(top_cc.symbol.to_list()):
    #   if not os.path.exists(f"OHLCV_1d/{symbol}_1d.json"):
    #     url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={symbol}&tsym=USD&allData=true&api_key={CC_API}"
    #     res = ses.get(url)
    #     try:
    #       price_df = pd.DataFrame(res.json().get("Data").get("Data"))[["time","open","high","close","low","volumeto"]]
    #       price_df.rename(columns={"volumeto":"volume"},inplace=True)
    #       price_df = price_df.query("(close > 0) and (open > 0) and (high > 0) and (low > 0)")
    #       available_OHLCV.append(symbol)
    #     except:
    #       print(f"missing ohlcv of {symbol}")
    #       price_df = pd.DataFrame([[np.nan]*6],columns=["time","open","high","close","low","volume"])
    #     price_df.to_json(f"OHLCV_1d/{symbol}_1d.json",orient="records")
    #   else:
    #     old_price_df = pd.read_json(f"OHLCV_1d/{symbol}_1d.json")
    #     url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={symbol}&tsym=USD&allData=true&api_key={CC_API}"
    #     res = ses.get(url)
    #     try:
    #       price_df = pd.DataFrame(res.json().get("Data").get("Data"))[["time","open","high","close","low","volumeto"]]
    #       price_df.rename(columns={"volumeto":"volume"},inplace=True)
    #       price_df = price_df.query("(close > 0) and (open > 0) and (high > 0) and (low > 0)")
    #       available_OHLCV.append(symbol)
    #     except:
    #       print(f"missing ohlcv of {symbol}")
    #       price_df = pd.DataFrame([[np.nan]*6],columns=["time","open","high","close","low","volume"])
    #     pd.concat([old_price_df,price_df]).drop_duplicates().to_json(f"OHLCV_1d/{symbol}_1d.json",orient="records")
    # with open(f"main_page/available_OHLCV.json", "w") as f:
    #   json.dump(list(set(available_OHLCV)),f)

    CMC2CC = {"AGIX":"AGI"} # Cryptocompare currently use this temporary name
    fromCryptoDotCom = ["BONE"] # Cryptocompare not have CCAAGG data, use only data from crypto.com
    if not os.path.exists("OHLCV_1h"):
      os.mkdir("OHLCV_1h")
    existed_OHLCV = glob.glob("OHLCV_1h/*")
    existed_symbols = [filename.split("/")[1].split("_")[0] for filename in existed_OHLCV]
    new_symbols = top_cc.symbol.to_list()
    all_symbols = list(set(existed_symbols+new_symbols))
    for symbol in tqdm(all_symbols):
      if not os.path.exists(f"OHLCV_1h/{symbol}_1h.json"):
        old_price_df = pd.DataFrame([[np.nan]*6],columns=["time","open","high","close","low","volume"])
      else:
        old_price_df = pd.read_json(f"OHLCV_1h/{symbol}_1h.json")
      if symbol in CMC2CC.keys():
        url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={CMC2CC[symbol]}&tsym=USD&limit=2000&api_key={CC_API}"
      elif symbol in fromCryptoDotCom:
        url = f"https://min-api.cryptocompare.com/data/v2/histohour?aggregate=1&e=cryptodotcom&fsym={symbol}&tryConversion=false&tsym=USD&api_key={CC_API}"
      else:
        url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={symbol}&tsym=USD&limit=2000&api_key={CC_API}"
      res = ses.get(url)
      try:
        price_df = pd.DataFrame(res.json().get("Data").get("Data"))[["time","open","high","close","low","volumeto"]]
        price_df.rename(columns={"volumeto":"volume"},inplace=True)
        price_df = price_df.query("(close > 0) and (open > 0) and (high > 0) and (low > 0)")
      except:
        print(f"missing ohlcv of {symbol}")
        price_df = pd.DataFrame([[np.nan]*6],columns=["time","open","high","close","low","volume"])
      pd.concat([old_price_df,price_df]).drop_duplicates(subset="time", keep="last").to_json(f"OHLCV_1h/{symbol}_1h.json",orient="records",indent=2)

    if not os.path.exists(f"main_page/Price7d"):
      os.mkdir(f"main_page/Price7d")
    
    for symbol in tqdm(all_symbols):
      price_df = pd.read_json(f"OHLCV_1h/{symbol}_1h.json")
      price_df = price_df[["time","close"]]
      price_df.iloc[-(24*7):].to_json(f"main_page/Price7d/{symbol}.json",orient="records",indent=2)
      
      if not os.path.exists(f"coin_page/{symbol}"):
        os.mkdir(f"coin_page/{symbol}")
      resdf.query("symbol==@symbol").to_json(f"coin_page/{symbol}/market_data.json",orient="records",indent=2)
      
    if os.path.exists("utils/available_assets.json"):
      with open("utils/available_assets.json","r") as f:
        existed_asset = json.load(f)
    else:
      existed_asset = []
    available_assets = list(set(existed_asset+all_symbols))
    with open("utils/available_assets.json","w") as f:
      json.dump(available_assets,f,indent=2)
      
    print("Update main page complete")
      
  except Exception as e:
    print("Fail to update main page data")
    print(e)

if __name__ == "__main__":
  generate_main_page()
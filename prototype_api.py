from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import timedelta, tzinfo, datetime as dt
from collections import OrderedDict
import pandas as pd
import json, os, time

OHLCV_AGG = OrderedDict((
    ('Open', 'first'),
    ('High', 'max'),
    ('Low', 'min'),
    ('Close', 'last'),
    ('Volume', 'sum'),
))

description = '''
    Prototype API for coinint
'''

app = FastAPI(title="Coinint API",
              description=description,
              version = '0.1')

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ErrorDetail(BaseModel):
    detail: str
    class Config:
        schema_extra = {'example': {"detail":"Some error message"}}

@app.get("/data/all/cryptocurrencis", 
    responses = {200:{"description": "Array of all available cryptocurrencis for coinpage"},
                 400:{"model":ErrorDetail}}
)
def get_all_cryptocurrencies():
    """
    Get the array of all available cryptocurrencis for coinpage.
    """
    slug_to_symbol = {"bitcoin":"BTC", "ethereum":"ETH", "uniswap":"UNI", "aave":"AAVE", "tether":"USDT"}
    all_coin = []
    for k,v in slug_to_symbol.items():
        all_coin.append({"slug":k,
                         "symbol":v})
    return all_coin

@app.get("/marketdata/overview",
    responses = {200:{"description": "market data for overview section"},
                 400:{"model":ErrorDetail}}
)
def get_marketdata_overview():
    """
    Get market data for overview section
    """
    with open(f"main_page/market_overview.json") as f:
        market_overview = json.load(f)
    return market_overview

@app.get("/marketdata/heatmap", 
    responses = {200:{"description": "market data for displaying heatmap"},
                 400:{"model":ErrorDetail}}
)
def get_marketdata_heatmap(limit : int = 25):
    """
    Get market data for displaying heatmap \n
    Parameter: \n
        limit : number of currencies to be shown, default is 25. [fully support <=25 for prototype version.]
    """
    heatmap = pd.read_json("main_page/coin_ranking_table.json")
    if limit > heatmap.shape[0]:
        raise HTTPException(status_code=400, detail=f"Only supported limit is less than {heatmap.shape[0]}")
    return json.loads(heatmap.iloc[:limit].to_json(orient="records"))

@app.get("/marketdata/cointable", 
    responses = {200:{"description": "market data for displaying cointable"},
                 400:{"model":ErrorDetail}}
)
def get_marketdata_cointable(limit : int = 25):
    """
    Get market data for displaying cointable \n
    Parameter: \n
        limit : number of currencies to be shown, default is 25. [only support <=25 for prototype version]
    """
    cointable = pd.read_json("main_page/coin_ranking_table.json")
    if limit > cointable.shape[0]:
        raise HTTPException(status_code=400, detail=f"Only supported limit is less than {cointable.shape[0]}")
    market_data = json.loads(cointable.iloc[:limit].to_json(orient="records"))
    for i in range(len(market_data)):
        with open(f"main_page/Price7d/{market_data[i]['symbol']}.json") as f:
            chart = json.load(f)
        market_data[i]["7day_chart"] = chart
    return market_data

@app.get("/highlight/gainers-losers", 
    responses = {200:{"description": "market data for gainers and losers"},
                 400:{"model":ErrorDetail}}
)
def get_highlight_gainer_losers(resolution : str = "24h", coin_rank_limit : int = 25, limit: int = 30):
    """
    Get market data for gainers and losers \n
    Parameter: \n
        resolution : timeframe/ period of time (1h, 24h, 7d, 30d), default = 24h. \n
        coin_rank_limit : maximum number of coin ranks (25,50,100,500), default = 25 \n
        limit : number of currencies to be shown only support 30 for prototype version.
    """
    if resolution not in ['1h','24h','7d','30d']:
        raise HTTPException(status_code=400, detail=f"Only supported resolution is '1h','24h','7d','30d'")
    if coin_rank_limit not in [25,50,100,500]:
        raise HTTPException(status_code=400, detail=f"Only supported coin_rank_limit is 25,50,100,500")
    with open(f"main_page/gainers_losers_{resolution}_top{coin_rank_limit}.json") as f:
        gainer_losers = json.load(f)
    return gainer_losers

@app.get("/highlight/trending", 
    responses = {200:{"description": "market data for trending coin"},
                 400:{"model":ErrorDetail}}
)
def get_highlight_trending(resolution : str = "24h", limit : int = 30):
    """
    Get market data for trending coin (NOTE: This is mocked data by randomly select 30 asset as trending coins) \n
    Parameter: \n
        resolution : timeframe/ period of time (24h, 7d, 30d), default = 24h. \n
        limit : number of currencies to be shown only support 30 for prototype version.
    """
    if resolution not in ['24h','7d','30d']:
        raise HTTPException(status_code=400, detail=f"Only supported resolution is '24h','7d','30d'")
    with open(f"main_page/trending_{resolution}.json") as f:
        trending = json.load(f)
    return trending

@app.get("/cryptocurrencies/{symbol}", 
    responses = {200:{"description": "Data and route for coindetail page for selected symbol"},
                 400:{"model":ErrorDetail},
                 404:{"model":ErrorDetail}}
)
def get_cryptocurrencies(symbol):
    """
    Get Data and route for coindetail page for selected symbol \n
    Parameter: \n
        symbol : seleceted asset symbol name.
    """
    if not os.path.exists(f"coin_page/{symbol}/metadata.json"):
        raise HTTPException(status_code=404, detail=f"{symbol} not found")
    with open(f"coin_page/{symbol}/metadata.json") as f:
        metadata = json.load(f)
    if "Stablecoin" in metadata["categories"]:
        cryptotype = "stablecoin"
    elif "Coin" in metadata["categories"]:
        cryptotype = "coin"
    elif "Token" in metadata["categories"]:
        cryptotype = "token"
    else:
        raise HTTPException(status_code=400, detail=f"Unknown type of cryptocurrencies")
    if cryptotype in ["coin","token"]:
        with open(f"coin_page/{symbol}/token_links.json") as f:
            token_links = json.load(f)
        with open(f"coin_page/{symbol}/what_is.json") as f:
            what_is = json.load(f)
        with open(f"coin_page/{symbol}/team.json") as f:
            team = json.load(f)
        with open(f"coin_page/{symbol}/investor.json") as f:
            investor = json.load(f)
        with open(f"coin_page/{symbol}/token_distribution.json") as f:
            token_distribution = json.load(f)
        overview = {}
        overview["data"] = {}
        overview["data"]["metadata"] = metadata
        overview["data"]["token_links"] = token_links
        overview["data"]["what_is"] = what_is
        overview["data"]["investor"] = investor
        overview["data"]["team"] = team
        overview["data"]["token_distribution"] = token_distribution
        overview["data"]["market_data"] = get_market_data(symbol)
        overview["data"]["price_chart"] = get_price_chart(symbol)
        overview["data"]["technical_analysis"] = get_technical_analysis(symbol)
        overview["data"]["key_metric"] = get_key_metric(symbol)
        overview["data"]["news_feed"] = get_key_metric(symbol)

        overview["route"] = {}
        overview["route"]["market_data"] = f"/cryptocurrencies/{symbol}/market_data"
        overview["route"]["price_chart"] = f"/cryptocurrencies/{symbol}/price_chart"
        overview["route"]["technical_analysis"] = f"/cryptocurrencies/{symbol}/technical_analysis"
        overview["route"]["key_metric"] = f"/cryptocurrencies/{symbol}/key_metric"
        overview["route"]["news_feed"] = f"/cryptocurrencies/{symbol}/news_feed"
    elif cryptotype in ["stablecoin"]:
        with open(f"coin_page/{symbol}/token_links.json") as f:
            token_links = json.load(f)
        with open(f"coin_page/{symbol}/what_is.json") as f:
            what_is = json.load(f)
        with open(f"coin_page/{symbol}/team.json") as f:
            team = json.load(f)
        with open(f"coin_page/{symbol}/investor.json") as f:
            investor = json.load(f)
        with open(f"coin_page/{symbol}/token_distribution.json") as f:
            token_distribution = json.load(f)
        overview = {}
        overview["data"] = {}
        overview["data"]["metadata"] = metadata
        overview["data"]["token_links"] = token_links
        overview["data"]["what_is"] = what_is
        overview["data"]["investor"] = investor
        overview["data"]["team"] = team
        overview["data"]["token_distribution"] = token_distribution
        overview["data"]["market_data"] = get_market_data(symbol)
        overview["data"]["price_chart"] = get_price_chart(symbol)
        overview["data"]["key_metric"] = get_key_metric(symbol)
        overview["data"]["news_feed"] = get_key_metric(symbol)

        overview["route"] = {}
        overview["route"]["market_data"] = f"/cryptocurrencies/{symbol}/market_data"
        overview["route"]["price_chart"] = f"/cryptocurrencies/{symbol}/price_chart"
        overview["route"]["key_metric"] = f"/cryptocurrencies/{symbol}/key_metric"
        overview["route"]["news_feed"] = f"/cryptocurrencies/{symbol}/news_feed"
    return overview

@app.get("/cryptocurrencies/{symbol}/market_data", 
    responses = {200:{"description": "market data for coin detail page of selected symbol "},
                 400:{"model":ErrorDetail},
                 404:{"model":ErrorDetail}}
)
def get_market_data(symbol):
    """
    Get dynamic market data for coin detail page of selected symbol \n
    Parameter: \n
        symbol : seleceted asset symbol name.
    """
    if not os.path.exists(f"coin_page/{symbol}/metadata.json"):
        raise HTTPException(status_code=404, detail=f"{symbol} not found")
    with open(f"coin_page/{symbol}/market_data.json") as f:
        market_data = json.load(f)[0]
    return market_data

@app.get("/cryptocurrencies/{symbol}/price_chart", 
    responses = {200:{"description": "price chart for coin detail page of selected symbol"},
                 400:{"model":ErrorDetail},
                 404:{"model":ErrorDetail}}
)
def get_price_chart(symbol, data_range: str = "7d"):
    """
    Get dynamic price chart for coin detail page of selected symbol \n
    Parameter: \n
        symbol : seleceted asset symbol name. \n
        data_range : data range ['7d','1m','3m','1y','all']
    """
    if data_range not in ['7d','1m','3m','1y','all']:
        raise HTTPException(status_code=400, detail=f"Only supported data range is '7d','1m','3m','1y','all'")
    if not os.path.exists(f"coin_page/{symbol}/metadata.json"):
        raise HTTPException(status_code=404, detail=f"{symbol} not found")
    with open(f"coin_page/{symbol}/price_chart_{data_range.casefold()}.json") as f:
        price_chart = json.load(f)
    return price_chart

@app.get("/cryptocurrencies/{symbol}/key_metric", 
    responses = {200:{"description": "key metric for coin detail page of selected symbol "},
                 400:{"model":ErrorDetail},
                 404:{"model":ErrorDetail}}
)
def get_key_metric(symbol, data_range: str = "7d"):
    """
    Get dynamic key metric for coin detail page of selected symbol \n
    Parameter: \n
        symbol : seleceted asset symbol name. \n
        data_range : data range ['7d','1m','3m','1y','all']
    """
    if data_range not in ['7d','1m','3m','1y','all']:
        raise HTTPException(status_code=400, detail=f"Only supported data range is '7d','1m','3m','1y','all'")
    if not os.path.exists(f"coin_page/{symbol}/metadata.json"):
        raise HTTPException(status_code=404, detail=f"{symbol} not found")
    with open(f"coin_page/{symbol}/key_metric_{data_range.casefold()}.json") as f:
        key_metric = json.load(f)
    return key_metric

@app.get("/cryptocurrencies/{symbol}/technical_analysis", 
    responses = {200:{"description": "technical analysis of selected symbol"},
                 400:{"model":ErrorDetail},
                 404:{"model":ErrorDetail}}
)
def get_technical_analysis(symbol):
    """
    Get dynamic technical analysis of selected symbol \n
    Parameter: \n
        symbol : seleceted asset symbol name.
    """
    if not os.path.exists(f"coin_page/{symbol}/metadata.json"):
        raise HTTPException(status_code=404, detail=f"{symbol} not found")
    with open(f"coin_page/{symbol}/technical_analysis.json") as f:
        price_chart = json.load(f)
    return price_chart

@app.get("/cryptocurrencies/{symbol}/news_feed", 
    responses = {200:{"description": "news feed of selected symbol"},
                 400:{"model":ErrorDetail},
                 404:{"model":ErrorDetail}}
)
def get_news_feed(symbol):
    """
    Get dynamic news feed of selected symbol \n
    Parameter: \n
        symbol : seleceted asset symbol name.
    """
    if not os.path.exists(f"coin_page/{symbol}/metadata.json"):
        raise HTTPException(status_code=404, detail=f"{symbol} not found")
    with open(f"coin_page/{symbol}/news_feed.json") as f:
        news_feed = json.load(f)
    return news_feed

@app.get("/cryptocurrencies/{symbol}/OHLCV", 
    responses = {200:{"description": "OHLCV of selected symbol"},
                 400:{"model":ErrorDetail},
                 404:{"model":ErrorDetail}}
)
def get_OHLCV(symbol, resolution: str = "24h", countback : int = 0, start : int = 0, end : int = 0):
    """
    Get dynamic OHLCV of selected symbol \n
    Parameter: \n
        symbol : seleceted asset symbol name. \n
        resolution : resolution str of requested asset for example ['1h','2h','3h','4h','1d','2d,'3d,'4d','1w','1m'] \n
        countback : query specific number of candle of requested asset until now, if countback != 0, start will be ignored \n
        start : start unix timestamp in ms for query request asset, default is 0. \n
        end : end unix timestamp in ms for query request asset, default is now.
    """
    if not os.path.exists(f"coin_page/{symbol}/metadata.json"):
        raise HTTPException(status_code=404, detail=f"{symbol} not found")
    # with open(f"coin_page/{symbol}/OHLCV.json") as f:
    #     OHLCV = json.load(f)

    if end == 0:
        end = int(time.mktime(dt.now().timetuple())*1e3)

    if "w" in resolution.casefold():
        resample_phase = f"{resolution.upper()}-MON"
    elif "m" in resolution.casefold():
        resample_phase = f"{resolution.upper()}S"
    else:
        resample_phase = f"{resolution}"
        
    with open(f"coin_page/{symbol}/OHLCV.json") as f:
        OHLCV_df = pd.DataFrame(json.load(f))
    print(OHLCV_df)

    if countback != 0:
        OHLCV_df = OHLCV_df.query(f"time<={end}")
        OHLCV_df.index = pd.to_datetime(OHLCV_df.time,unit="ms")
        OHLCV_df.drop("time",axis=1,inplace=True)
        print(OHLCV_df)
        OHLCV_df = OHLCV_df.resample(resample_phase, label='left', closed='left').agg(OHLCV_AGG).dropna().iloc[-countback:,:]
    else:
        OHLCV_df = OHLCV_df.query(f"time<={end} and time >={start}")
        OHLCV_df.index = pd.to_datetime(OHLCV_df.time,unit="ms")
        OHLCV_df.drop("time",axis=1,inplace=True)
        print(OHLCV_df)
        OHLCV_df = OHLCV_df.resample(resample_phase, label='left', closed='left').agg(OHLCV_AGG).dropna()
    OHLCV_df["time"] = OHLCV_df.index
    return json.loads(OHLCV_df.to_json(orient="records"))

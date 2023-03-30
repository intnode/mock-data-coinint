from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import timedelta, tzinfo, datetime as dt
import pandas as pd
import json


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


@app.get("/marketdata/heatmap", 
    responses = {200:{"description": "market data for displaying heatmap"},
                 400:{"model":ErrorDetail}}
)
def get_marketdata_heatmap(limit : int = 25):
    """
    Get market data for displaying heatmap \n
    Parameter: \n
        limit : number of currencies to be shown, default is 25.
    """
    heatmap = pd.read_json("main_page/coin_ranking_table.json")
    if limit > heatmap.shape[0]:
        raise HTTPException(status_code=400, detail=f"Only supported limit is less than {heatmap.shape[0]}")
    return json.loads(heatmap.iloc[:limit].to_json(orient="records"))

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

@app.get("/marketdata/cointable", 
    responses = {200:{"description": "market data for displaying cointable"},
                 400:{"model":ErrorDetail}}
)
def get_marketdata_cointable(limit : int = 25):
    """
    Get market data for displaying cointable \n
    Parameter: \n
        limit : number of currencies to be shown, default is 25.
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

@app.get("/cryptocurrencies/{slug}", 
    responses = {200:{"description": "Data and route for coindetail page for selected slug"},
                 400:{"model":ErrorDetail}}
)
def get_cryptocurrencies(slug):
    """
    Get Data and route for coindetail page for selected slug \n
    Parameter: \n
        slug : seleceted asset slug name.
    """
    with open(f"coin_page/{slug}/metadata.json") as f:
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
        with open(f"coin_page/{slug}/token_links.json") as f:
            token_links = json.load(f)
        with open(f"coin_page/{slug}/what_is.json") as f:
            what_is = json.load(f)
        with open(f"coin_page/{slug}/team.json") as f:
            team = json.load(f)
        with open(f"coin_page/{slug}/investor.json") as f:
            investor = json.load(f)
        with open(f"coin_page/{slug}/token_distribution.json") as f:
            token_distribution = json.load(f)
        overview = {}
        overview["data"] = {}
        overview["data"]["metadata"] = metadata
        overview["data"]["token_links"] = token_links
        overview["data"]["what_is"] = what_is
        overview["data"]["investor"] = investor
        overview["data"]["team"] = team
        overview["data"]["token_distribution"] = token_distribution
        overview["data"]["market_data"] = get_market_data(slug)
        overview["data"]["price_chart"] = get_price_chart(slug)
        overview["data"]["technical_analysis"] = get_technical_analysis(slug)
        overview["data"]["key_metric"] = get_key_metric(slug)
        overview["data"]["news_feed"] = get_key_metric(slug)

        overview["route"] = {}
        overview["route"]["market_data"] = f"/cryptocurrencies/{slug}/market_data"
        overview["route"]["price_chart"] = f"/cryptocurrencies/{slug}/price_chart"
        overview["route"]["technical_analysis"] = f"/cryptocurrencies/{slug}/technical_analysis"
        overview["route"]["key_metric"] = f"/cryptocurrencies/{slug}/key_metric"
        overview["route"]["news_feed"] = f"/cryptocurrencies/{slug}/news_feed"
    elif cryptotype in ["stablecoin"]:
        with open(f"coin_page/{slug}/token_links.json") as f:
            token_links = json.load(f)
        with open(f"coin_page/{slug}/what_is.json") as f:
            what_is = json.load(f)
        with open(f"coin_page/{slug}/team.json") as f:
            team = json.load(f)
        with open(f"coin_page/{slug}/investor.json") as f:
            investor = json.load(f)
        with open(f"coin_page/{slug}/token_distribution.json") as f:
            token_distribution = json.load(f)
        overview = {}
        overview["data"] = {}
        overview["data"]["metadata"] = metadata
        overview["data"]["token_links"] = token_links
        overview["data"]["what_is"] = what_is
        overview["data"]["investor"] = investor
        overview["data"]["team"] = team
        overview["data"]["token_distribution"] = token_distribution
        overview["data"]["market_data"] = get_market_data(slug)
        overview["data"]["price_chart"] = get_price_chart(slug)
        overview["data"]["key_metric"] = get_key_metric(slug)
        overview["data"]["news_feed"] = get_key_metric(slug)

        overview["route"] = {}
        overview["route"]["market_data"] = f"/cryptocurrencies/{slug}/market_data"
        overview["route"]["price_chart"] = f"/cryptocurrencies/{slug}/price_chart"
        overview["route"]["key_metric"] = f"/cryptocurrencies/{slug}/key_metric"
        overview["route"]["news_feed"] = f"/cryptocurrencies/{slug}/news_feed"
    return overview

@app.get("/cryptocurrencies/{slug}/market_data", 
    responses = {200:{"description": "market data for coin detail page of selected slug "},
                 400:{"model":ErrorDetail}}
)
def get_market_data(slug):
    """
    Get dynamic market data for coin detail page of selected slug \n
    Parameter: \n
        slug : seleceted asset slug name.
    """
    with open(f"coin_page/{slug}/market_data.json") as f:
        market_data = json.load(f)[0]
    return market_data

@app.get("/cryptocurrencies/{slug}/price_chart", 
    responses = {200:{"description": "price chart for coin detail page of selected slug"},
                 400:{"model":ErrorDetail}}
)
def get_price_chart(slug, resolution: str = "7d"):
    """
    Get dynamic price chart for coin detail page of selected slug \n
    Parameter: \n
        slug : seleceted asset slug name.
    """
    if resolution not in ['7d','1m','3m','1y','all']:
        raise HTTPException(status_code=400, detail=f"Only supported resolution is '7d','1m','3m','1y','all'")
    with open(f"coin_page/{slug}/price_chart_{resolution.casefold()}.json") as f:
        price_chart = json.load(f)
    return price_chart

@app.get("/cryptocurrencies/{slug}/key_metric", 
    responses = {200:{"description": "key metric for coin detail page of selected slug "},
                 400:{"model":ErrorDetail}}
)
def get_key_metric(slug, resolution: str = "7d"):
    """
    Get dynamic key metric for coin detail page of selected slug \n
    Parameter: \n
        slug : seleceted asset slug name.
    """
    if resolution not in ['7d','1m','3m','1y','all']:
        raise HTTPException(status_code=400, detail=f"Only supported resolution is '7d','1m','3m','1y','all'")
    with open(f"coin_page/{slug}/key_metric_{resolution.casefold()}.json") as f:
        key_metric = json.load(f)
    return key_metric

@app.get("/cryptocurrencies/{slug}/technical_analysis", 
    responses = {200:{"description": "technical analysis of selected slug"},
                 400:{"model":ErrorDetail}}
)
def get_technical_analysis(slug):
    """
    Get dynamic technical analysis of selected slug \n
    Parameter: \n
        slug : seleceted asset slug name.
    """
    with open(f"coin_page/{slug}/technical_analysis.json") as f:
        price_chart = json.load(f)
    return price_chart

@app.get("/cryptocurrencies/{slug}/news_feed", 
    responses = {200:{"description": "news feed of selected slug"},
                 400:{"model":ErrorDetail}}
)
def get_news_feed(slug):
    """
    Get dynamic news feed of selected slug \n
    Parameter: \n
        slug : seleceted asset slug name.
    """
    with open(f"coin_page/{slug}/news_feed.json") as f:
        news_feed = json.load(f)
    return news_feed

@app.get("/cryptocurrencies/{slug}/OHLCV", 
    responses = {200:{"description": "OHLCV of selected slug"},
                 400:{"model":ErrorDetail}}
)
def get_OHLCV(slug):
    """
    Get dynamic OHLCV of selected slug \n
    Parameter: \n
        slug : seleceted asset slug name.
    """
    with open(f"coin_page/{slug}/OHLCV.json") as f:
        OHLCV = json.load(f)
    return OHLCV

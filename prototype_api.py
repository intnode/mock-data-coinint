from prototype_api import FastAPI, Body, HTTPException
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

@app.get("/marketdata/heatmap", 
    responses = {200:{"description": "OHLCV data of requested ticker"},
                 400:{"model":ErrorDetail}}
)
def get_marketdata_heatmap(limit : int = 25):
    """
    Get OHLCV historical data of requested ticker and exchange (or source) the input ticker must in the form of "{ticker_id}:{ticker_exchange} list of available tickers can be found with get /asset \n
    Parameter: \n
        limit : number of currencies to be shown, default is 25.
    """
    heatmap = pd.read_json("main_page/top_coin_ranking_table.json")
    if limit > heatmap.shape[0]:
        raise HTTPException(status_code=400, detail=f"Only supported limit is less than {heatmap.shape[0]}")
    return json.loads(heatmap.iloc[:limit].to_json(orient="records"))
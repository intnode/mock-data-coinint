from __future__ import print_function
import os, requests, csv, time, argparse
from bs4 import BeautifulSoup
from web3 import Web3
import pandas as pd

token_abi_dict = {"bsc":[{"inputs":[],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":True,"inputs":[],"name":"_decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"_name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"_symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"}]}
endpoint_dict = {"bsc":"https://bsc-dataseed4.binance.org"}

def getData(sess, URL, page):
    url = URL + page
    print("Retrieving page", page)
    return BeautifulSoup(sess.get(url,headers={'User-Agent': 'Mozilla/5.0'}).text, 'html.parser')

def getPage(sess, URL, page):
    table = getData(sess, URL, str(int(page))).find('table')
    try:
        data = [[X.text.strip() for X in row.find_all('td')] for row in table.find_all('tr')]
    except:
        data = None
    finally:
        return data

def main(network, address):
    explorer_url_dict = {"eth":f"https://etherscan.io/token/generic-tokenholders2?a={address}&s=0&p=",
                         "bsc":f"https://bscscan.com/token/generic-tokenholders2?a={address}&s=0&p="}
    web3 = Web3(Web3.HTTPProvider(endpoint_dict[network.casefold()]))
    contract = web3.eth.contract(address=address,abi=token_abi_dict[network.casefold()])
    token_symbol = contract.functions.symbol().call()
    total_supply = contract.functions.totalSupply().call()
    decimals = contract.functions.decimals().call()
    URL = explorer_url_dict[network.casefold()]
    filename = f"{token_symbol}_{network}_top_holder.csv"
    sess = requests.Session()
    print(f"Get top 1000 holders for {token_symbol} of {network}")
    all_data = []
    page = 0
    while True:
        page += 1
        data = getPage(sess, URL, page)
        if data == None:
            break
        else:
            for row in data:
                all_data.append(row)
            time.sleep(1)
    df = pd.DataFrame(all_data,columns= "Rank Address Quantity Percentage Value -".split()).replace("",None)
    df = df.dropna(axis=1,how="all").dropna(axis=0,how="all")
    df.Rank = df.Rank.astype(int)
    df.Quantity = df.Quantity.str.replace(',', '').astype(float)
    df.Value = df.Value.str.replace('\$|,', '', regex=True).astype(float)
    df.Percentage = df.Quantity/(total_supply/10**decimals)
    df.to_csv(filename, index=False)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run API for backtesting')
    parser.add_argument('--network', type=str, help='network name', default="bsc")
    parser.add_argument('--address' ,type=str, help='token address', default="0x2170Ed0880ac9A755fd29B2688956BD959F933F8")
    args = parser.parse_args()
    network = args.network
    address = args.address

    ################
    # network = "bsc"
    # address = "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"
    ################

    data = main(network, address)
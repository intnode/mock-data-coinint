from __future__ import print_function
import os, requests, csv, time, argparse, json
from bs4 import BeautifulSoup
from web3 import Web3
import pandas as pd
from io import StringIO
from tqdm import tqdm

token_abi_dict = {"bsc":[{"inputs":[],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":True,"inputs":[],"name":"_decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"_name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"_symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"}],
                  "eth":[{"constant":True,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"_upgradedAddress","type":"address"}],"name":"deprecate","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"deprecated","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"_evilUser","type":"address"}],"name":"addBlackList","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"upgradedAddress","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"","type":"address"}],"name":"balances","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"maximumFee","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"_totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"unpause","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"name":"_maker","type":"address"}],"name":"getBlackListStatus","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowed","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"paused","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"who","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"pause","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"getOwner","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"name":"newBasisPoints","type":"uint256"},{"name":"newMaxFee","type":"uint256"}],"name":"setParams","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"name":"amount","type":"uint256"}],"name":"issue","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"name":"amount","type":"uint256"}],"name":"redeem","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"basisPointsRate","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"","type":"address"}],"name":"isBlackListed","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"_clearedUser","type":"address"}],"name":"removeBlackList","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"MAX_UINT","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"name":"_blackListedUser","type":"address"}],"name":"destroyBlackFunds","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"_initialSupply","type":"uint256"},{"name":"_name","type":"string"},{"name":"_symbol","type":"string"},{"name":"_decimals","type":"uint256"}],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":False,"name":"amount","type":"uint256"}],"name":"Issue","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"amount","type":"uint256"}],"name":"Redeem","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"newAddress","type":"address"}],"name":"Deprecate","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"feeBasisPoints","type":"uint256"},{"indexed":False,"name":"maxFee","type":"uint256"}],"name":"Params","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"_blackListedUser","type":"address"},{"indexed":False,"name":"_balance","type":"uint256"}],"name":"DestroyedBlackFunds","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"_user","type":"address"}],"name":"AddedBlackList","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"_user","type":"address"}],"name":"RemovedBlackList","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"owner","type":"address"},{"indexed":True,"name":"spender","type":"address"},{"indexed":False,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"from","type":"address"},{"indexed":True,"name":"to","type":"address"},{"indexed":False,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":False,"inputs":[],"name":"Pause","type":"event"},{"anonymous":False,"inputs":[],"name":"Unpause","type":"event"}],
                  "avax":[{"inputs":[{"internalType":"address","name":"_logic","type":"address"},{"internalType":"address","name":"admin_","type":"address"},{"internalType":"bytes","name":"_data","type":"bytes"}],"stateMutability":"payable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"previousAdmin","type":"address"},{"indexed":False,"internalType":"address","name":"newAdmin","type":"address"}],"name":"AdminChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"beacon","type":"address"}],"name":"BeaconUpgraded","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"implementation","type":"address"}],"name":"Upgraded","type":"event"},{"stateMutability":"payable","type":"fallback"},{"inputs":[],"name":"admin","outputs":[{"internalType":"address","name":"admin_","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newAdmin","type":"address"}],"name":"changeAdmin","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"implementation","outputs":[{"internalType":"address","name":"implementation_","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"}],"name":"upgradeTo","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"upgradeToAndCall","outputs":[],"stateMutability":"payable","type":"function"},{"stateMutability":"payable","type":"receive"}]}
endpoint_dict = {"bsc":"https://bsc-dataseed4.binance.org",
                 "eth":"https://eth.llamarpc.com",
                 "avax":"https://avalanche.public-rpc.com"}

headers = {'User-Agent': 'Mozilla/5.0'}

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def getData(sess, URL, page):
    url = URL + page
    print("Retrieving page", page)
    return BeautifulSoup(sess.get(url,headers=headers).text, 'html.parser')

def getPage(sess, URL, page):
    table = getData(sess, URL, str(int(page))).find('table')
    try:
        data = [[X.text.strip() for X in row.find_all('td')] for row in table.find_all('tr')]
    except:
        data = None
    finally:
        return data

def getTopHolders(network, address, get_coin):
    if network in ["btc"]:
        symbol = "BTC"
        url = "https://api.blockchair.com/bitcoin/stats"
        req_stats = requests.get(url, headers=headers)
        while req_stats.status_code != 200:
            print("API hit limit, wait for 1min")
            time.sleep(60)
            req_stats = requests.get(url, headers=headers)
        print(req_stats.text)
        total_holders = req_stats.json()["data"]["hodling_addresses"]
        cur_supply = req_stats.json()["data"]["circulation"]/10**8
        url = "https://api.blockchair.com/bitcoin/addresses?limit=100"
        req_address = requests.get(url, headers=headers)
        time.sleep(10)
        print(len(req_address.json().get("data")))
        while req_address.status_code != 200 or len(req_address.json().get("data")) == 0:
            print("API hit limit, wait for 2min")
            time.sleep(120)
            req_address = requests.get(url, headers=headers)
        df = pd.DataFrame(req_address.json().get("data"))
        print(df)
        df.balance = df.balance/10**8    
        df["Percentage"] = df.balance/cur_supply
        holder_stat = {}
        holder_stat["total_holders"] = total_holders
        for n in [10,20,50,100]:
            holder_stat[f"top_{n}_holders"] = df.iloc[:n].Percentage.sum()
    else:
        if get_coin:
            explorer_coin_url_dict = {
                "eth":f"https://etherscan.io/accounts/",
                "bsc":f"https://bscscan.com/accounts/",
                "avax":f"https://snowtrace.io/accounts/"
            }
            explorer_chart_url_dict = {
                "eth":f"https://etherscan.io/chart/address?output=csv",
                "bsc":f"https://bscscan.com/chart/address?output=csv",
                "avax":f"https://snowtrace.io/chart/address?output=csv"
            }
            URL = explorer_coin_url_dict[network.casefold()]
            sess = requests.Session()
            print(f"Get top 1000 address for {network}")
            all_data = []
            page = 0
            while True and page < 40:
                page += 1
                data = getPage(sess, URL, page)
                if data == None:
                    break
                else:
                    for row in data:
                        all_data.append(row)
                    time.sleep(1)
            df = pd.DataFrame(all_data,columns= ["Rank", "Address", "Name Tag", "Quantity" ,"Percentage", "Txn Count"])
            df = df.replace("--",None)
            df = df.dropna(axis=1,how="all").dropna(axis=0,how="all")
            df = df.dropna(axis=0,how="any",subset=["Percentage"])
            symbol = df.Quantity.iloc[0].split(" ")[1]
            df.Rank = df.Rank.astype(int)
            df.Quantity = df.Quantity.str.replace(symbol, '').str.replace(',', '').astype(float)
            df.Percentage = df.Percentage.str.replace('\%|,', '', regex=True).astype(float)/100
            df["Txn Count"] = df["Txn Count"].str.replace(',', '', regex=True).astype(int)
            filename = f"{symbol}_{network}_top_holder.csv"
            df.to_csv(filename, index=False)
            total_address_df = pd.read_csv(StringIO(requests.get(explorer_chart_url_dict[network], headers=headers).text), sep=",")
            holder_stat = {}
            holder_stat["total_holders"] = int(total_address_df.iloc[-1].Value)
            for n in [10,20,50,100]:
                holder_stat[f"top_{n}_holders"] = float(df.iloc[:n].Percentage.sum())
        else:
            explorer_url_dict = {"eth":f"https://etherscan.io/token/generic-tokenholders2?a={address}&s=0&p=",
                                "bsc":f"https://bscscan.com/token/generic-tokenholders2?a={address}&s=0&p=",
                                "avax":f"https://snowtrace.io/token/generic-tokenholders2?a={address}&s=0&p="}
            web3 = Web3(Web3.HTTPProvider(endpoint_dict[network.casefold()]))
            contract = web3.eth.contract(address=address,abi=token_abi_dict[network.casefold()])
            symbol = contract.functions.symbol().call()
            total_supply = contract.functions.totalSupply().call()
            decimals = contract.functions.decimals().call()
            URL = explorer_url_dict[network.casefold()]
            filename = f"{symbol}_{network}_top_holder.csv"
            sess = requests.Session()
            print(f"Get top 1000 holders for {symbol} of {network}")
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
            
            txt = sess.get(URL,headers={'User-Agent': 'Mozilla/5.0'}).text
            start_all_holder_idx = txt.find("From a total")
            end_all_holder_idx = txt.find("holders",start_all_holder_idx)
            all_holder_txt = txt[start_all_holder_idx:end_all_holder_idx]
            holder_stat = {}
            holder_stat["total_holders"] = int(all_holder_txt.split(" ")[-2].replace(",",""))
            for n in [10,20,50,100]:
                holder_stat[f"top_{n}_holders"] = float(df.iloc[:n].Percentage.sum())
        
    with open(f"coin_page/{symbol}/holders_statistics.json","w") as f:
        json.dump(holder_stat,f)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='get top holder for each chain')
    parser.add_argument('--run-all' ,type=str2bool, nargs='?', const=True, help='get all available coin for prototype', default=False)
    parser.add_argument('--network', type=str, help='network name', default="bsc")
    parser.add_argument('--get-coin' ,type=str2bool, nargs='?', const=True, help='get network coin', default=False)
    parser.add_argument('--address' ,type=str, help='token address', default="0x2170Ed0880ac9A755fd29B2688956BD959F933F8")
    args = parser.parse_args()
    network = args.network
    address = args.address
    get_coin = args.get_coin
    run_all = args.run_all

    ################
    # network = "bsc"
    # address = "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"
    # get_coin = True
    ################
    if not args.run_all:
        data = getTopHolders(network, address, get_coin)
    else:
        for network, address, get_coin in tqdm([('btc','',True),
                                                ('avax','',True),
                                                ('eth','',True),
                                                ('eth','0xdAC17F958D2ee523a2206206994597C13D831ec7',False),
                                                ('eth','0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',False),
                                                ('eth','0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',False)]):
            data = getTopHolders(network, address, get_coin)
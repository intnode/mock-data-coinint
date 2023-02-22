from coin_detail import generate_coin_details
from main_page import generate_main_page

if __name__ == "__main__":
  asset_list = ["BTC", "ETH", "UNI", "AAVE", "USDT"]
  generate_main_page(asset_list)
  generate_coin_details(asset_list)
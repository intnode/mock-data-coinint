from coin_detail import generate_coin_details
from main_page import generate_main_page
import os, schedule, uvicorn, threading, time, datetime, argparse
from datetime import datetime as dt

asset_list = ["BTC", "ETH", "UNI", "AAVE", "USDT"]

def get_time():
    """
    get current time for checking that updating thread is still alive.
    """
    print(dt.now())
    
def run_continuously(interval=1):
    """
    create thread for running schedule task in a background.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

if __name__ == "__main__":
    """
    All of database updating services should be abandon once the database of coinint is complete.
    """
    parser = argparse.ArgumentParser(description='Run API for backtesting')
    parser.add_argument('--host', type=str, help='host, [default=127.0.0.1]', default="127.0.0.1")
    parser.add_argument('--port', type=int, help='port, [default=6600]', default=6600)
    parser.add_argument('--workers', type=int, help='number of workers, [default=1]', default=1)
    parser.add_argument('--debug', type=bool, help='debug mode, [default=False]', default=False)
    parser.add_argument('--updater', type=bool, help='run db updating service in background, [default=True]', default=True)
    args = parser.parse_args() 

    if args.debug:
        print(f"Running API in debug mode")
        uvicorn.run("prototype_api:app", host="127.0.0.1", port=6600, reload=args.debug)
    else:
        if args.updater:
            print(f"Updating database before starting API")
            generate_main_page(asset_list)
            generate_coin_details(asset_list)
            schedule.every().hour.at("00:00").do(generate_main_page,asset_list)
            schedule.every().hour.at("00:00").do(generate_coin_details,asset_list)
            schedule.every().minute.at(":00").do(get_time)
            schedule.run_all()
            print(f"Updating is completed, start to running the API")
            run_background_schedule = run_continuously() # Make all schedules updating run in a background
            uvicorn.run("prototype_api:app", host=args.host, port=args.port, workers=args.workers)
            run_background_schedule.set()
        else:
            uvicorn.run("prototype_api:app", host=args.host, port=args.port, workers=args.workers)
'''
This code is written by Jack Hou @ GTSI
It aims at capturing real-time stock data from the Internet and store the data into csv file
2022/11/29
'''

import pandas as pd
from database import *
import yfinance as yf
import time
import numpy as np
from indicator import Stock

def from_yahoo(ticker, start, end):
    if (ticker or start or end) is None: return
    start_time = time.time()
    print("Downloading {} from {} to {} ...".format(ticker, start, end))
    df = yf.download(ticker, start = start, end = end, progress = False)
    print(df.head())
    print("{} from {} to {} downloaded".format(ticker, start, end))
    csv = "D:\\Codebase\\fintech\\data\\{}.csv".format(ticker)
    df.to_csv(csv, index = True)
    df = pd.read_csv(csv)
    my_stock = Stock(df)
    df["Average"] = (df["High"] + df["Low"]) * 0.5
    df["Volume"] = df["Volume"]
    df["Value"] = df["Volume"] * df["Average"]
    df['MA5'] = my_stock.cal_mat()
    df['CHMF'] = my_stock.cal_CHMF()
    df["Upper"], df["Lower"] = my_stock.cal_up_lower()
    df["BBH"], df["BBM"], df["BBL"] = my_stock.cal_bollinger_bands()
    df['OBV'] = my_stock.cal_OBV()
    df['RSI'] = my_stock.cal_RSI()
    df["DIF"], df["MACD"], df["DFF"]= my_stock.cal_MACD()
    df['IR'] = my_stock.read_IR(2018, 12)
    # df['VIX'] = my_stock.read_VIX("01/03/2011", "12/27/2018")
    # df["PCR"] = my_stock.read_PCR("2011/1/3", "2018/12/27")
    df['VIX'] = my_stock.read_VIX("01/02/2018", "12/27/2018")
    df["PCR"] = my_stock.read_PCR("2018/1/2", "2018/12/27")
    
    df['KL'], df['DL'] = my_stock.cal_KDLines()
    df['OUD'], df["CUD"] = my_stock.cal_trend(mode="Open"), my_stock.cal_trend(mode="Close")
    df.to_csv("D:\\Codebase\\fintech\\data\\{}.csv".format(ticker), index = True)
    my_stock = Stock(df)
    df["RPB"], df["MACDC"], df["Candlestick"], df["KDLine"], df["OBVC"], df["RSIP"], df["PCRP"], df["PCRC"], df["RSIC"] = my_stock.determine_state()
    df.to_csv("D:\\Codebase\\fintech\\data\\{}-state.csv".format(ticker), index = True)
    print("{} written.".format(csv))
    end_time = time.time()
    print("{:.3f}s elapsed.\n".format(end_time - start_time))


    




def to_mysql(host, user, password, database, ticker):
    if (database or ticker) is None: return
    # each time, the columns need to be re-defined as long as new indicators have been added
    table_columns = {'DateTime': 'datetime',
                     'Open': 'DECIMAL(32,16)',
                     'High': 'DECIMAL(32,16)',
                     'Low': 'DECIMAL(32,16)',
                     'Close': 'DECIMAL(32,16)',
                     'Adj_Close': 'DECIMAL(32,16)',
                     'Volume': 'BIGINT',
                     'MA5': 'DECIMAL(32,16)',
                     'CHMF': 'DECIMAL(32,16)',
                     'BBL': 'DECIMAL(32,16)',
                     'BBH': 'DECIMAL(32,16)',
                     'OBV': 'BIGINT',
                     'RSI': 'DECIMAL(32,16)',
                     'MACD': 'DECIMAL(32,16)',
                     'FLAG': 'BIGINT',
                     'IR': 'DECIMAL(32,16)',
                     'VIX': 'DECIMAL(32,16)',
                     'KL': 'DECIMAL(32,16)',
                     'DL': 'DECIMAL(32,16)',
                     'UD': 'DECIMAL(32,16)',
                     "STATE": "BIGINT",
                     }
    primary_key = 'DateTime'

    db = mysql(host=host, user=user, password=password)
    db.create_database(database)
    print("Processing {} ...".format(ticker))
    table = ticker
    csv = "./data/{}.csv".format(ticker)
    df = pd.read_csv(csv, index_col = False)

    print("database: {}".format(database))
    print("table: {}".format(table))


    db.create_table(database, table, table_columns, primary_key)
    db.insert_items(database, table, [tuple(df.loc[idx].values) for idx in df.index])

if __name__ == "__main__":
    # tickers = ['AAPL', 'BIDU', 'MSFT', 'TSLA']
    tickers = ['TQQQ']
    for ticker in tickers:
        # from_yahoo(ticker, '2011-01-03', '2018-12-28')
        from_yahoo(ticker, '2018-1-02', '2018-12-28')
        # to_mysql("localhost", "root", "houjiacheng", "stock_min", "LABU")
 
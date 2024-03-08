#!/usr/bin/env python
# coding: utf-8

# In[5]:


# -*- coding: utf-8 -*-
import os, sys
import shutil
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.optimize import curve_fit
import threading
import random
from multiprocessing import Process
from bithumbAPI import XCoinAPI
from RecordModel import *
from Filter import *
import datetime
from pytz import timezone
import json


class MyWindow:
    def __init__(self, menu):
        ## bithumb ##
        access_key = ''
        secret_key = ''

        self.api = XCoinAPI(access_key, secret_key)

        self.dat_T = "10m"
        self.sell_min = 3
        self.sell_seconds = self.sell_min * 60
        self.buy_min = int(self.sell_min)
        self.buy_seconds = self.buy_min * 60

        self.top_n = 10
        self.basic_price = 20000

        self.shadow = False


        if menu=="exec":
            #timeout = Process(target=self.do(self.sell_seconds, self.buy_seconds, self.sell_timeout, self.buy_timeout))
            #timeout.start()
            #timeout.join()

            sell_timeout = Process(target=self.sell_timeout_timer)
            #buy_timeout = Process(target=self.buy_timeout_timer)
            sell_timeout.start()
            #buy_timeout.start()
            sell_timeout.join()
            #buy_timeout.join()

        elif menu=="backtest":
            self.start = 0
            self.term = 100
            self.end = self.term

            self.backtest()

        elif menu=="shadow":
            self.shadow = True
            timeout = Process(target=self.do(self.sell_seconds, self.buy_seconds, self.sell_timeout, self.buy_timeout))
            timeout.start()
            timeout.join()

    def backtest(self):
        tickers = self.get_tickers()
        high_price = np.array(np.array(self.get_chart(tickers, self.dat_T))[:,3]).astype(float)
        low_price = np.array(np.array(self.get_chart(tickers, self.dat_T))[:,4]).astype(float)

    def get_chart(self, ticker, unitT):
        endpoint = "/public/candlestick/" + ticker + "_KRW" + "/" + unitT
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","chart_intervals":unitT}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)["data"]
        return result

    def get_tickers(self):
        endpoint = "/public/ticker/ALL_KRW"
        params = {"endpoint":endpoint,"payment_currency":"KRW"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)["data"].keys()
        return list(result)

    def get_balance(self, ticker):
        endpoint = "/info/balance"
        params = {"endpoint":endpoint,"currency":ticker}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)["data"]["available_"+ticker.lower()]
        return result

    def post_market_sell(self, ticker, units):
        endpoint = "/trade/market_sell"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","units":units}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        return result

    def post_market_buy(self, ticker, units):
        endpoint = "/trade/market_buy"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","units":units}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        return result

    def post_order_buy(self, ticker, units, price):
        endpoint = "/trade/place"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","units":units,"price":price,"type":"bid"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        return result

    def post_order_sell(self, ticker, units, price):
        endpoint = "/trade/place"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","units":units,"price":price,"type":"ask"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        return result

    def post_buy_cancel(self, order_id, ticker):
        endpoint = "/trade/cancel"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","order_id":order_id,"type":"bid"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        return result

    def post_sell_cancel(self, order_id, ticker):
        endpoint = "/trade/cancel"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","order_id":order_id,"type":"ask"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        return result

    def sell_timeout_timer(self):
        while 1:
            self.sell_timeout()
            time.sleep(self.sell_seconds + random.randint(0, 10))

    def buy_timeout_timer(self):
        while 1:
            self.buy_timeout()
            time.sleep(self.buy_seconds + random.randint(0, 10))


    @staticmethod
    def timer(sec, sec2, function, function2, condition):        
        cnt_sec_buf = 0
        cnt_sec2_buf = 0
        function2()
        while 1:
            sec_buf = sec + random.randint(0, 10)
            cnt_sec_buf += sec_buf

            function()
            time.sleep(sec_buf)

            if cnt_sec_buf > sec2:
                cnt_sec2_buf += cnt_sec_buf
                cnt_sec_buf = 0

                function2()
                time.sleep(random.randint(0, 10))

            if condition:
                print('timer end..')
                break

    def do(self, sec, sec2, function, function2, condition=False):
        self.timer(sec, sec2, function, function2, condition)

    def sell_timeout(self):
        print("\nsell log start!", file=open("sell_log.txt", "a"))

        mm = int(datetime.datetime.now(timezone('Asia/Seoul')).strftime("%M"))
        # print(mm, mm % 30, "sell")
        '''if mm % 30 < 19 or 23 <= mm % 30 < 30:
            return 1'''

        '''if mm == 0 or 6 <= mm < 60:
            return 1'''

        sell_id_f = open("sell_id.txt", "r")
        sell_id_list = sell_id_f.read().split("\n")
        sell_id_f.close()

        for row in sell_id_list:
            try:
                sell_id, ticker, amount_, price_ = row.split()
                sell_cancel_res = self.post_sell_cancel(sell_id, ticker)
                # sell_market_res = self.post_market_sell(ticker, amount_)
                print(sell_cancel_res, sell_market_res)
            except:
                continue
        
        sell_id_f = open("sell_id.txt", "w")
        sell_id_f.writelines([])
        sell_id_f.close()

        tickers = self.get_tickers()
        result = dict()
        amount_refer = dict()
        price_refer = dict()
        for ticker in tickers:
            mm = int(datetime.datetime.now(timezone('Asia/Seoul')).strftime("%M"))
            hhmm = int(datetime.datetime.now(timezone('Asia/Seoul')).strftime("%H%M"))
        
            '''if mm % 30 < 19 or 23 <= mm % 30 < 30:
                return 1'''

            '''if mm == 0 or 6 <= mm < 60:
                return 1'''
            
            try:
                balance = float(int(float(self.get_balance(ticker)) * 10**4) / 10**4)
                if balance < 0.0001 or self.shadow==True:
                    continue

                # print("\nsell log : ", ticker, file=open("sell_log.txt", "a"))
                amount_refer[ticker] = balance

                raw_data = np.array(self.get_chart(ticker, self.dat_T))
                
                current_timestamp = int(datetime.datetime.fromtimestamp(int(raw_data[:,0][-1]) / 1000).strftime("%H%M"))
                
                '''if hhmm // 10 != current_timestamp // 10:
                    print(f"{ticker} : {current_timestamp}, current : {hhmm}", file=open("sell_log.txt", "a"))
                    continue'''

                close_price = np.array(raw_data[:,2]).astype(float)
                low_price = np.array(raw_data[:,4]).astype(float)
                volume = np.array(raw_data[:,5]).astype(float)
                trans_money = close_price * volume
                '''if np.mean(trans_money[-3:]) < 20000 or balance * close_price[-1] < 40000:
                    continue'''

                price_refer[ticker] = close_price[-1]

                #judge_buf = basic_model_wrap(close_price[-60:], 1.0)
                #judge_buf = chunk_judge(close_price[-100:], 40)
                #judge_buf = chunk_judge2(close_price[-2:], 2, 1, 0, 0, 1)
                #judge_buf2 = chunk_judge2(volume[-2:], 2, 1, 0, 0, 1)
                #judge_buf3 = chunk_judge2(low_price[-2:], 2, 1, 0, 0, 1)
                
                #if judge_buf == "sell" and judge_buf2 == "sell" and judge_buf3 == "sell":
                if True:
                    result[ticker] = 1
                    print("sell :",ticker, file=open("sell_log.txt", "a"))
            except:
                pass

        fin_result = sorted(result.items(), key=lambda x:x[1], reverse=True)
        fin_tickers = list(map(lambda x:x[0], fin_result))
        for ticker in fin_tickers:
            try:
                if self.shadow==False:
                    sell_res = self.post_market_sell(ticker, amount_refer[ticker])
                    # sell_res = self.post_order_sell(ticker, amount_refer[ticker], price_refer[ticker])
                    sell_id = sell_res['order_id']
                    print(sell_id, ticker, amount_refer[ticker], price_refer[ticker], file=open("sell_id.txt", "a"))
                print(ticker, "MARKET SELL :", price_refer[ticker], result[ticker], file=open("log.txt", "a"))
            except:
                print(ticker + " : market sell error..")
                pass

        return 0
    

if __name__ == "__main__":
    # menu = input("exec / shadow: ")
    menu = "exec"
    myWindow = MyWindow(menu=menu)

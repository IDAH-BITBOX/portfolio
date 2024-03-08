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
import smtplib
from email.mime.text import MIMEText
# from basic import *


class MyWindow:
    def __init__(self, menu):
        ## bithumb ##
        access_key = ''
        secret_key = ''

        self.api = XCoinAPI(access_key, secret_key)

        self.dat_T = "10m"
        self.dat_min = 10
        self.sell_min = 10
        self.timing_ths = 0.5

        self.sell_seconds = self.sell_min * 60
        self.buy_min = int(self.sell_min)
        self.buy_seconds = self.buy_min * 60

        self.top_n = 1000
        self.basic_price = 10000

        self.shadow = False

        if menu=="exec":
            #timeout = Process(target=self.do(self.sell_seconds, self.buy_seconds, self.sell_timeout, self.buy_timeout))
            #timeout.start()
            #timeout.join()

            sell_timeout = Process(target=self.sell_timeout_timer)
            buy_timeout = Process(target=self.buy_timeout_timer)
            sell_timeout.start()
            buy_timeout.start()
            sell_timeout.join()
            buy_timeout.join()

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
        time.sleep(0.1)
        return result
    
    def get_hoga(self, ticker):
        endpoint = "/public/orderbook/" + ticker + "_KRW"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params, method="get")["data"]
        time.sleep(0.1)
        return result

    def get_tickers(self):
        endpoint = "/public/ticker/ALL_KRW"
        params = {"endpoint":endpoint,"payment_currency":"KRW"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)["data"].keys()
        time.sleep(0.1)
        return list(result)

    def get_balance(self, ticker):
        endpoint = "/info/balance"
        params = {"endpoint":endpoint,"currency":ticker}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)["data"]["available_"+ticker.lower()]
        time.sleep(0.1)
        return result

    def get_krw_balance(self):
        endpoint = "/info/balance"
        params = {"endpoint":endpoint,"currency":"btc"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)["data"]["total_krw"]
        time.sleep(0.1)
        return result

    def post_market_sell(self, ticker, units):
        endpoint = "/trade/market_sell"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","units":units}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        time.sleep(0.1)
        return result

    def post_market_buy(self, ticker, units):
        endpoint = "/trade/market_buy"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","units":units}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        time.sleep(0.1)
        return result

    def post_order_buy(self, ticker, units, price):
        endpoint = "/trade/place"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","units":units,"price":price,"type":"bid"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        time.sleep(0.1)
        return result

    def post_order_sell(self, ticker, units, price):
        endpoint = "/trade/place"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","units":units,"price":price,"type":"ask"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        time.sleep(0.1)
        return result

    def post_buy_cancel(self, order_id, ticker):
        endpoint = "/trade/cancel"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","order_id":order_id,"type":"bid"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        time.sleep(0.1)
        return result

    def post_sell_cancel(self, order_id, ticker):
        endpoint = "/trade/cancel"
        params = {"endpoint":endpoint,"order_currency":ticker,"payment_currency":"KRW","order_id":order_id,"type":"ask"}
        result = self.api.xcoinApiCall(endpoint=endpoint, rgParams=params)
        time.sleep(0.1)
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
            sec_buf = sec# + random.randint(0, 10)
            cnt_sec_buf += sec_buf

            function()
            time.sleep(sec_buf)

            if cnt_sec_buf > sec2:
                cnt_sec2_buf += cnt_sec_buf
                cnt_sec_buf = 0

                function2()
                #time.sleep(random.randint(0, 10))

            if condition:
                print('timer end..')
                break

    def do(self, sec, sec2, function, function2, condition=False):
        self.timer(sec, sec2, function, function2, condition)

    def sell_timeout(self):
        print("\nsell log start!", file=open("sell_log.txt", "a"))
        now = datetime.datetime.now(timezone('Asia/Seoul'))
        mm = int(now.strftime("%M"))
        hhmm = int(now.strftime("%H%M"))
        # print(mm, mm % 30, "sell")
        '''if mm % 30 < 19 or 23 <= mm % 30 < 30:
            return 1'''

        '''if mm == 0 or 6 <= mm < 60:
            return 1'''

        '''if hhmm % 1200 == 0 or 6 <= hhmm % 1200 < 1200:
            return 1'''

        hold_f = open("hold.txt", "r")
        hold = hold_f.read().strip("\n").strip().split("\n")
        hold_f.close()
        
        hold_refer = dict()
        sell_history = []
        for row in hold:
            if len(row.strip("\n").strip().split())==0:
                continue
            buy_id_, ticker_, amount_, price_, hhmm_, unit_time_ = row.strip("\n").strip().split()
            hold_time_ = hhmm - int(hhmm_)
            if hold_time_ < 0:
                    hold_time_ += 2400
            if int(unit_time_) > 0:
                if ticker_ in hold_refer:
                    hold_refer[ticker_].append([buy_id_, ticker_, float(amount_), float(price_), int(hhmm_), int(unit_time_)])
                else:
                    hold_refer[ticker_] = [[buy_id_, ticker_, float(amount_), float(price_), int(hhmm_), int(unit_time_)]]
            else:
                '''if ticker_ not in sell_history:
                    balance_ = float(int(float(self.get_balance(ticker_)) * 10**4) / 10**4)
                    sell_res = self.post_market_sell(ticker_, balance_)
                    sell_history.append(ticker_)
                    print("sell :",ticker_, file=open("sell_log.txt", "a"))'''
                pass
        
        pos_target_f = open("pos_target.txt", "r")
        pos_target_ = pos_target_f.read().strip("\n").strip().split("\n")
        pos_target_f.close()

        pos_target_refer = dict()
        for row in pos_target_:
            if len(row.strip("\n").strip().split())==0:
                continue
            ticker, target = row.strip("\n").strip().split()
            if ticker in pos_target_refer:
                pos_target_refer[ticker].append(float(target))
            else:
                pos_target_refer[ticker] = [float(target)]

        neg_target_f = open("neg_target.txt", "r")
        neg_target_ = neg_target_f.read().strip("\n").strip().split("\n")
        neg_target_f.close()

        neg_target_refer = dict()
        for row in neg_target_:
            if len(row.strip("\n").strip().split())==0:
                continue
            ticker, target = row.strip("\n").strip().split()
            if ticker in neg_target_refer:
                neg_target_refer[ticker].append(float(target))
            else:
                neg_target_refer[ticker] = [float(target)]

        sell_id_f = open("sell_id.txt", "r")
        sell_id_list = sell_id_f.read().split("\n")
        sell_id_f.close()

        for row in sell_id_list:
            try:
                sell_id, ticker, amount_, price_ = row.split()
                sell_cancel_res = self.post_sell_cancel(sell_id, ticker)
                balance = float(int(float(self.get_balance(ticker)) * 10**4) / 10**4)
                if balance >= 0.001:
                    #print(ticker, file=open("order_penalty_count.txt", "a"))
                    #sell_market_res = self.post_market_sell(ticker, amount_)
                    #print(sell_cancel_res, sell_market_res)
                    pass
            except:
                continue
        
        sell_id_f = open("sell_id.txt", "w")
        sell_id_f.writelines([])
        sell_id_f.close()

        ## order_penalty_count tickers load ##
        order_penalty_count_f = open("order_penalty_count.txt", "r")
        order_penalty_count = order_penalty_count_f.read().strip().strip("\n").split("\n")
        order_penalty_count_f.close()
        order_penalty_count_dict = dict()
        for ticker in order_penalty_count:
            if ticker in order_penalty_count_dict:
                order_penalty_count_dict[ticker] += 1
            else:
                order_penalty_count_dict[ticker] = 1
        order_penalty_count_dict = sorted(order_penalty_count_dict.items(), key=lambda x:x[1], reverse=True)
        order_penalty_count_lst = list(map(lambda x:x[0], order_penalty_count_dict))[:20]

        tickers = self.get_tickers()
        result = dict()
        amount_refer = dict()
        price_refer = dict()
        log_df = pd.DataFrame(columns=['ticker', 'price', 'balance', 'updatedAt'])
        log_tot_df = pd.DataFrame(columns=['total_krw', 'total_ticker_cnt', 'updated_at'])
        total_krw = float(self.get_krw_balance())
        total_ticker_cnt = 0

        np.random.shuffle(tickers)

        for ticker in tickers:
            now = datetime.datetime.now(timezone('Asia/Seoul'))
            mm = int(now.strftime("%M"))
            hhmm = int(now.strftime("%H%M"))
            mmddhhmm = int(now.strftime("%m%d%H%M"))
        
            '''if mm % 30 < 19 or 23 <= mm % 30 < 30:
                return 1'''

            '''if (int(hhmm // 100) != 11 and int(hhmm // 100) != 23) or mm < 30 or mm >= 45:
                return 1'''
            
            '''if mm == 0 or 6 <= mm < 60:
                return 1'''
            
            '''if hhmm % 1200 == 0 or 6 <= hhmm % 1200 < 1200:
                return 1'''

            try:
                balance = float(int(float(self.get_balance(ticker)) * 10**4) / 10**4)
                if balance < 0.0001 or self.shadow==True:
                    continue

                if ticker not in hold_refer:
                    continue
                    
                hoga = self.get_hoga(ticker)
                buy_hoga_price = list(map(lambda x:float(x['price']), hoga['bids']))
                sell_hoga_price = list(map(lambda x:float(x['price']), hoga['asks']))
                if (min(sell_hoga_price) - max(buy_hoga_price)) / max(buy_hoga_price) * 100 > 0.1:
                    continue

                amount_refer[ticker] = balance

                raw_data = np.array(self.get_chart(ticker, self.dat_T))
                
                current_timestamp = int(datetime.datetime.fromtimestamp(int(raw_data[:,0][-1]) / 1000).strftime("%m%d%H%M"))
                
                close_price = list(np.array(raw_data[:,2]).astype(float))
                high_price = list(np.array(raw_data[:,3]).astype(float))
                low_price = list(np.array(raw_data[:,4]).astype(float))
                volume = list(np.array(raw_data[:,5]).astype(float))
                
                delta = mmddhhmm - current_timestamp
                delta_idx = int(delta / self.dat_min)
                
                close_price = np.array(close_price)
                high_price = np.array(high_price)
                low_price = np.array(low_price)
                volume = np.array(volume)

                trans_money = close_price * volume
                amount = round(self.basic_price / close_price[-1], 4)

                total_krw += balance * close_price[-1]
                total_ticker_cnt += 1

                price_refer[ticker] = close_price[-1]

                #judge_buf = basic_model_wrap(close_price[-60:], 1.0)
                #judge_buf = chunk_judge(close_price[-100:], 40)
                #judge_buf = chunk_judge2(close_price[-2:], 2, 1, 0, 0, 1)
                #judge_buf2 = chunk_judge2(volume[-2:], 2, 1, 0, 0, 1)
                #judge_buf3 = chunk_judge2(high_price[-2:], 2, 1, 0, 0, 1)
                #judge_buf4 = chunk_judge2(low_price[-2:], 2, 1, 0, 0, 1)
                #pro_judge = basic_model_wrap(close_price[-30:], 7, 1.0)
                N = 4
                W = 3
                M = 2
                diffusion_check = 1000
                coef = 1
                buy_condition = "lower_record"
                sell_condition = "upper_record"

                if len(close_price) < N:
                    continue

                #ratio = 1.3
                #pro_judge_close = record_statistics(close_price[-N:], 2, ratio)
                #pro_judge_close = stack_regime_judge(close_price[-N:], W, M, diffusion_check) # regime_judge(low_price[-N:], 2, diffusion_check)
                #pro_judge_close = regime_judge(close_price[-W:], M, diffusion_check)
                #pro_judge_close = basic_model_new(close_price[-N:], W, M, diffusion_check, coef)
                pro_judge_close = chunk_model_judge_new(close_price[-N:], W, M, diffusion_check, buy_condition, sell_condition)

                scaled_timing_check = 0.0
                buy_id_, ticker_, amount_, price_, hhmm_, unit_time_ = hold_refer[ticker][-1]
                hold_time_ = mmddhhmm - hhmm_
                delta_check = current_timestamp - hhmm_
                scaled_timing_check += unit_time_ - hold_time_

                benefit = (float(close_price[-1]) - float(price_)) / float(price_)
                if ticker in pos_target_refer and len(pos_target_refer[ticker]) > 10 and np.mean(pos_target_refer[ticker]) > 0.1:
                    pos_target = np.mean(pos_target_refer[ticker])
                else:
                    pos_target = 0.1
                if ticker in neg_target_refer and len(neg_target_refer[ticker]) > 10 and np.mean(neg_target_refer[ticker]) < -0.1:
                    neg_target = np.mean(neg_target_refer[ticker])
                else:
                    neg_target = -0.1

                if scaled_timing_check > self.timing_ths:
                    print(ticker, scaled_timing_check, self.timing_ths, file=open("sell_timing_persist_log.txt", "a"))
                    continue

                if (scaled_timing_check <= self.timing_ths and delta_check > 0) and pro_judge_close=="sell": # or benefit < neg_target):
                    if benefit < neg_target:
                        print(ticker, file=open("order_penalty_count.txt", "a"))
                    if pro_judge_close=="sell":
                        if benefit > 0:
                            print(ticker, benefit, file=open("pos_target.txt", "a"))
                        elif benefit < 0:
                            print(ticker, benefit, file=open("neg_target.txt", "a"))

                    result[ticker] = 1
                    log_df_buf = pd.DataFrame(columns=['ticker', 'price', 'balance', 'updatedAt'])
                    log_df_buf['ticker'] = [ticker]
                    log_df_buf['price'] = [close_price[-1]]
                    log_df_buf['balance'] = [balance]
                    log_df_buf['updatedAt'] = [datetime.datetime.now(timezone('Asia/Seoul'))]
                    log_df = pd.concat([log_df, log_df_buf], axis=0)
                    
                    try:
                        if self.shadow==False:
                            '''if ticker in order_penalty_count_lst:
                                sell_res = self.post_market_sell(ticker, amount_refer[ticker])
                            else:'''
                            #sell_res = self.post_order_sell(ticker, amount_refer[ticker], price_refer[ticker])
                            sell_res = self.post_market_sell(ticker, amount_refer[ticker])
                            sell_id = sell_res['order_id']
                            print(sell_id, ticker, amount_refer[ticker], price_refer[ticker], file=open("sell_id.txt", "a"))
                            print(sell_id, ticker, amount_refer[ticker], price_refer[ticker], mmddhhmm, -1, file=open("hold.txt", "a"))
                            print("sell :",ticker, file=open("sell_log.txt", "a"))
                        print(ticker, "MARKET SELL :", price_refer[ticker], result[ticker], file=open("log.txt", "a"))
                    except:
                        print(ticker + " : market sell error..", file=open("sell_log.txt", "a"))
                        pass
            except:
                pass

        log_tot_df['total_krw'] = [total_krw]
        log_tot_df['total_ticker_cnt'] = [total_ticker_cnt]
        log_tot_df['updated_at'] = [datetime.datetime.now(timezone('Asia/Seoul'))]

        #insert_df_to_db(True, "tracking_balance", log_df)
        #insert_df_to_db(True, "total_balance", log_tot_df)

        return 0

    def buy_timeout(self):
        #today = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
        print("\nbuy log start!", file=open("buy_log.txt", "a"))

        mm = int(datetime.datetime.now(timezone('Asia/Seoul')).strftime("%M"))
        hhmm = int(datetime.datetime.now(timezone('Asia/Seoul')).strftime("%H%M"))
        # print(mm, mm % 30)
        '''if mm % 30 < 23 or 28 <= mm % 30 < 30:
            return 1'''

        '''if mm < 6 or 11 <= mm < 60:
            return 1'''
        
        '''if hhmm % 1200 < 6 or 11 <= hhmm % 1200 < 1200:
            return 1'''

        buy_id_f = open("buy_id.txt", "r")
        buy_id_list = buy_id_f.read().split("\n")
        buy_id_f.close()

        for row in buy_id_list:
            try:
                buy_id, ticker, amount_, price_ = row.split()
                buy_cancel_res = self.post_buy_cancel(buy_id, ticker)
                balance = float(int(float(self.get_balance(ticker)) * 10**4) / 10**4)
                if balance < 0.0001:
                    pass
                    #print(ticker, file=open("order_penalty_count.txt", "a"))
                    #buy_market_res = self.post_market_buy(ticker, amount_)
                    #print(buy_cancel_res, buy_market_res)
            except:
                continue
        
        buy_id_f = open("buy_id.txt", "w")
        buy_id_f.writelines([])
        buy_id_f.close()

        ## filtered_tickers save ##
        # transaction_end_filter()

        ## filtered_tickers load ##
        must_not_buy_f = open("must_not_buy.txt", "r")
        must_not_buy = must_not_buy_f.read().split("\n")
        must_not_buy_f.close()

        ## order_penalty_count tickers load ##
        order_penalty_count_f = open("order_penalty_count.txt", "r")
        order_penalty_count = order_penalty_count_f.read().strip().strip("\n").split("\n")
        order_penalty_count_f.close()
        order_penalty_count_dict = dict()
        for ticker in order_penalty_count:
            if ticker in order_penalty_count_dict:
                order_penalty_count_dict[ticker] += 1
            else:
                order_penalty_count_dict[ticker] = 1
        order_penalty_count_dict = sorted(order_penalty_count_dict.items(), key=lambda x:x[1], reverse=True)
        order_penalty_count_lst = list(map(lambda x:x[0], order_penalty_count_dict))[:20]
        
        tickers = self.get_tickers()
        result = dict()
        amount_refer = dict()
        price_refer = dict()
        
        log_df = pd.DataFrame(columns=['ticker', 'price', 'balance', 'updatedAt'])

        np.random.shuffle(tickers)

        for ticker in tickers:
            now = datetime.datetime.now(timezone('Asia/Seoul'))
            mm = int(now.strftime("%M"))
            hhmm = int(now.strftime("%H%M"))
            mmddhhmm = int(now.strftime("%m%d%H%M"))

            
            '''if mm % 30 < 23 or 28 <= mm % 30 < 30:
                return 1'''
            
            '''if (int(hhmm // 100) != 11 and int(hhmm // 100) != 23) or mm < 45:
                return 1'''

            '''if mm < 6 or 11 <= mm < 60:
                return 1'''

            '''if hhmm % 1200 < 6 or 11 <= hhmm % 1200 < 1200:
                return 1'''
            
            try:
                if ticker in must_not_buy:
                    continue

                if ticker in order_penalty_count_lst:
                    continue

                raw_data = np.array(self.get_chart(ticker, self.dat_T))
                # print(datetime.datetime.fromtimestamp(int(raw_data[:,0][-1]) / 1000))
                current_timestamp = int(datetime.datetime.fromtimestamp(int(raw_data[:,0][-1]) / 1000).strftime("%m%d%H%M"))

                '''if hhmm // 10 != current_timestamp // 10:
                    print(f"{ticker} : {current_timestamp}, current : {hhmm}", file=open("buy_log.txt", "a"))
                    continue'''

                close_price = list(np.array(raw_data[:,2]).astype(float))
                high_price = list(np.array(raw_data[:,3]).astype(float))
                low_price = list(np.array(raw_data[:,4]).astype(float))
                volume = list(np.array(raw_data[:,5]).astype(float))
                
                delta = mmddhhmm - current_timestamp
                delta_idx = int(delta / self.dat_min)
                
                close_price = np.array(close_price)
                high_price = np.array(high_price)
                low_price = np.array(low_price)
                volume = np.array(volume)

                trans_money = close_price * volume
                amount = round(self.basic_price / close_price[-1], 4)
                balance = float(int(float(self.get_balance(ticker)) * 10**4) / 10**4)

                if balance < 0.0001:
                    amount_refer[ticker] = amount
                else:
                    #amount_refer[ticker] = balance
                    amount_refer[ticker] = amount

                if close_price[-1] < 0.01: # or np.mean(trans_money[-3:]) < self.basic_price: # or np.mean(trans_money[-3:]) < amount_refer[ticker]: # amount < 0.001 or 
                    print("Filtered! :", ticker, np.mean(trans_money[-3:]), np.mean(trans_money[-30:]), self.basic_price, file=open("buy_log.txt", "a"))
                    continue

                hoga = self.get_hoga(ticker)
                buy_hoga_price = list(map(lambda x:float(x['price']), hoga['bids']))
                sell_hoga_price = list(map(lambda x:float(x['price']), hoga['asks']))
                if (min(sell_hoga_price) - max(buy_hoga_price)) / max(buy_hoga_price) * 100 > 0.1:
                    continue

                price_refer[ticker] = close_price[-1]

                #judge_buf = basic_model_wrap(close_price[-60:], 1.0)
                #judge_buf = chunk_judge(close_price[-100:], 40)
                #judge_buf = chunk_judge2(close_price[-2:], 2, 1, 0, 0, 1)
                #judge_buf2 = chunk_judge2(volume[-2:], 2, 1, 0, 0, 1)
                #judge_buf3 = chunk_judge2(high_price[-2:], 2, 1, 0, 0, 1)
                #judge_buf4 = chunk_judge2(low_price[-2:], 2, 1, 0, 0, 1)
                #pro_judge = basic_model_wrap(close_price[-30:], 7, 1.0)
                N = 4
                W = 3
                M = 2
                diffusion_check = 1000
                coef = 1
                buy_condition = "lower_record"
                sell_condition = "upper_record"

                if len(close_price) < N:
                    continue

                #ratio = 1.3
                #pro_judge_close = record_statistics(close_price[-N:], 2, ratio)
                #pro_judge_close = stack_regime_judge(close_price[-N:], W, M, diffusion_check) # regime_judge(low_price[-N:], 2, diffusion_check)
                #pro_judge_close = regime_judge(close_price[-W:], M, diffusion_check)
                #pro_judge_close = basic_model_new(close_price[-N:], W, M, diffusion_check, coef)
                pro_judge_close = chunk_model_judge_new(close_price[-N:], W, M, diffusion_check, buy_condition, sell_condition)


                if pro_judge_close=="buy":
                    result[ticker] = -trans_money[-1]
                    log_df_buf = pd.DataFrame(columns=['ticker', 'price', 'balance', 'updatedAt'])
                    log_df_buf['ticker'] = [ticker]
                    log_df_buf['price'] = [close_price[-1]]
                    log_df_buf['balance'] = [balance + amount]
                    log_df_buf['updatedAt'] = [datetime.datetime.now(timezone('Asia/Seoul'))]
                    log_df = pd.concat([log_df, log_df_buf], axis=0)
                    try:
                        if self.shadow==False:
                            buy_res = self.post_market_buy(ticker, amount_refer[ticker])
                            #buy_res = self.post_order_buy(ticker, amount_refer[ticker], price_refer[ticker])
                            buy_id = buy_res['order_id']
                            print(buy_id, ticker, amount_refer[ticker], price_refer[ticker], file=open("buy_id.txt", "a"))
                            print(buy_id, ticker, amount_refer[ticker], price_refer[ticker], mmddhhmm, self.dat_min, file=open("hold.txt", "a")) ## delta -> delta + self.dat_min 실험해볼 것
                            print("buy :",ticker, file=open("buy_log.txt", "a"))
                        print(ticker, "MARKET BUY :", price_refer[ticker], result[ticker], file=open("log.txt", "a"))
                    except:
                        print(ticker + " : market buy error..", file=open("buy_log.txt", "a"))
                        pass
            except:
                pass

        #insert_df_to_db(True, "tracking_buy_balance", log_df)
        
        return 0


if __name__ == "__main__":
    # menu = input("exec / shadow: ")
    menu = "exec"
    myWindow = MyWindow(menu=menu)

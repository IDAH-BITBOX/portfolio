import json
import requests
import time
import datetime
import numpy as np
import pandas as pd
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import bindparam
from sqlalchemy.sql import text
from sqlalchemy import MetaData, Table, select, delete, update
from urllib.parse import quote
import matplotlib.pyplot as plt
import pybithumb
from tqdm import tqdm
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


tickers = pybithumb.get_tickers()

def bithumb_data(tickers, start, chart_intervals):
    data = []
    for ticker in tqdm(tickers):
        try:
            df = pybithumb.get_candlestick(ticker, chart_intervals=chart_intervals)[:]
        except:
            continue
        now = datetime.datetime.now()

        df['Date'] = df.index
        df.index = np.arange(len(df))
        holder = np.zeros(6000)
        log_ret = np.log(df['close'].values)
        log_ret = log_ret[1:] - log_ret[:-1]
        if len(log_ret) > 0:
            holder[-len(log_ret):] = log_ret
            data.append(holder)
        time.sleep(0.1)
    data = np.array(data)
    
    now = datetime.datetime.now()
    delta = now - start
    days = delta.days
    hours = delta.seconds / 60 / 60
    idx = days*24 + hours
    idx = int(idx * 60 / 3 + 1)
    
    mean_data = np.exp(np.mean(np.cumsum(data[:,-idx:], axis=1), axis=0)) - 1.0
    high_data = np.exp((np.max(np.cumsum(data[:,-idx:], axis=1), axis=0)*0.05 + np.mean(np.cumsum(data[:,-idx:], axis=1), axis=0)*1.95)/2) - 1.0
    low_data = np.exp((np.min(np.cumsum(data[:,-idx:], axis=1), axis=0)*0.05 + np.mean(np.cumsum(data[:,-idx:], axis=1), axis=0)*1.95)/2) - 1.0
    
    return mean_data, high_data, low_data

def add_subplot_axes(ax,rect,axisbg='w'):
    fig = plt.gcf()
    box = ax.get_position()
    width = box.width
    height = box.height
    inax_position  = ax.transAxes.transform(rect[0:2])
    transFigure = fig.transFigure.inverted()
    infig_position = transFigure.transform(inax_position)    
    x = infig_position[0]
    y = infig_position[1]
    width *= rect[2]
    height *= rect[3]  # <= Typo was here
    #subax = fig.add_axes([x,y,width,height],facecolor=facecolor)  # matplotlib 2.0+
    subax = fig.add_axes([x,y,width,height])
    x_labelsize = subax.get_xticklabels()[0].get_size()
    y_labelsize = subax.get_yticklabels()[0].get_size()
    x_labelsize *= rect[2]**0.5
    y_labelsize *= rect[3]**0.5
    subax.xaxis.set_tick_params(labelsize=x_labelsize)
    subax.yaxis.set_tick_params(labelsize=y_labelsize)
    return subax

DB_URI = ""

develop_uri = f'mysql+mysqlconnector://{DB_URI}'
deploy_uri = f'mysql+mysqlconnector://{DB_URI}'

def read_sql_pandas(con, stmt):
    result_df = pd.DataFrame()
    start_time = time.time()
    for df in pd.read_sql(stmt, con, chunksize=50000):
        result_df = pd.concat([result_df, df])
    print(len(result_df), time.time()-start_time)
    result_df.index = np.arange(len(result_df))
    return result_df

def load_db_to_df(engineType, tableName , cols):
    if engineType:
        engine = create_engine(deploy_uri)
    else:
        engine = create_engine(develop_uri)
    engine = engine.execution_options(autocommit=True)
    with engine.begin() as conn:
        print('SELECT ' + ', '.join(cols) + ' FROM ' + tableName)
        result_df = read_sql_pandas(conn, tableName)
        conn.close()
    engine.dispose()
    return result_df

def draw_pic(interval):
    start = datetime.datetime.strptime("2024-01-29 23:10:00", "%Y-%m-%d %H:%M:%S")
    plt.ion()
    fig, ax = plt.subplots(figsize=(20,10))
    rect = [0.0,0.3,0.25,0.4]
    ax1 = add_subplot_axes(ax, rect)
    while True:
        df_total = load_db_to_df(1, "total_balance", [])
        df_total = df_total[df_total['updated_at'] > start]
        print(len(df_total))

        mean_data, high_data, low_data = bithumb_data(tickers, start, "3m")

        accnt = np.log(df_total['total_krw'].values[-1]/df_total['total_krw'].values[0])

        print(f"My Accnt:{round((np.exp(accnt) - 1.0)*100, 3)}%\nMarket:{round(mean_data[-1]*100, 3)}%")

        ax.clear()
        ax1.clear()

        ax.plot(df_total['updated_at'].values, df_total['total_krw'].values, label=f"My Accnt:{round((np.exp(accnt) - 1.0)*100, 3)}%\nMarket:{round(mean_data[-1]*100, 3)}%")

        ax1.bar(np.arange(1, len(mean_data)+1), high_data-mean_data,width=0.8,bottom=mean_data,color="blue",alpha=0.5)
        ax1.bar(np.arange(1, len(mean_data)+1), mean_data-low_data,width=0.8,bottom=low_data,color="red",alpha=0.5)
        ax1.plot(np.arange(1, len(mean_data)+1), mean_data, color="black")

        ax.set_ylabel("Won")
        ax.set_xlabel("t")
        ax.legend(fontsize=20)
        plt.legend(fontsize=20)
        plt.savefig("model_fig.png")

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('', '')
        msg = MIMEMultipart()
        msg_text = MIMEText(f'{start.strftime("%Y-%m-%d %H:%M:%S")} ~ {datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")} 기준')
        msg['Subject'] = "암호화폐 모델 성과 보고"
        msg['To'] = ''
        with open("model_fig.png","rb") as f:
            image = f.read()
            mime_img = MIMEImage(image)
        msg.attach(msg_text)
        msg.attach(mime_img)
        smtp.sendmail('', '', msg.as_string())  
        smtp.quit()
        plt.pause(interval)

if __name__ == "__main__":
    draw_pic(60 * 60)
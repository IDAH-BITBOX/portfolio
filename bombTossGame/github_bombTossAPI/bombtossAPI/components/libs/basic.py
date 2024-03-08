import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import quote
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import bindparam
from sqlalchemy.sql import text
from sqlalchemy import MetaData, Table, select, delete, update
import pandas as pd
import numpy as np
import json
from math import ceil
from functools import wraps
import sqlalchemy as sa
import time
from pytz import timezone
from fastapi import HTTPException


## Basic Functions ##

DB_URI = ""

deploy_uri = f'mysql+mysqlconnector://{DB_URI}'
develop_uri = f'mysql+mysqlconnector://{DB_URI}'


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def week_of_month(dt):
    dt = datetime.datetime.strptime(dt, "%Y-%m-%d")
    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))


def read_sql_pandas(con, stmt):
    result_df = pd.DataFrame()
    start_time = time.time()
    for df in pd.read_sql(stmt, con, chunksize=50000):
        result_df = pd.concat([result_df, df])
    # print(len(result_df), time.time()-start_time)
    result_df.index = np.arange(len(result_df))
    return result_df


def write_sql_pandas(con, argv):
    stmt, df = argv
    result = df.to_sql(name=stmt, con=con, if_exists='append', index=False, method="multi")
    return result


def load_db_to_df(engineType, tableName , cols):
    if engineType:
        engine = create_engine(deploy_uri)
    else:
        engine = create_engine(develop_uri)
    engine = engine.execution_options(autocommit=False)
    with engine.begin() as conn:
        # print('SELECT ' + ', '.join(cols) + ' FROM ' + tableName)
        result_df = read_sql_pandas(conn, tableName)
        conn.close()
    engine.dispose()
    return result_df


def insert_df_to_db(engineType, tableName, df, method='append'):
    if engineType:
        engine = create_engine(deploy_uri)
    else:
        engine = create_engine(develop_uri)
    engine = engine.execution_options(autocommit=False)
    with engine.begin() as conn:
        write_sql_pandas(conn, (tableName, df))
        conn.commit()
        conn.close()
    engine.dispose()
    # print("insert rows: ",len(df))
    return 200


def load_db(engineType, tableName, cond):
    if engineType:
        engine = create_engine(deploy_uri)
    else:
        engine = create_engine(develop_uri)
    engine = engine.execution_options(autocommit=False)
    with engine.begin() as conn:
        query_basic = "SELECT * FROM " + str(tableName) + " WHERE "
        for key_, val_ in cond.items():
            query_basic += str(key_) + " = " + str(val_) + " AND "
        query_basic = query_basic.strip(" AND ")
        query_basic += ";"
        # print(query_basic)
        query = text(query_basic)
        result = conn.execute(query).fetchall()
        conn.commit()
        conn.close()
    engine.dispose()
    return pd.DataFrame(result)


def load_db_query(engineType, query_basic):
    if engineType:
        engine = create_engine(deploy_uri)
    else:
        engine = create_engine(develop_uri)
    engine = engine.execution_options(autocommit=False)
    with engine.begin() as conn:
        # print(query_basic)
        query = text(query_basic)
        result = conn.execute(query).fetchall()
        conn.commit()
        conn.close()
    engine.dispose()
    return pd.DataFrame(result)


def patch_db(engineType, tableName, obj, cond):
    if engineType:
        engine = create_engine(deploy_uri)
    else:
        engine = create_engine(develop_uri)
    engine = engine.execution_options(autocommit=False)
    with engine.begin() as conn:
        for key, val in obj.items():
            query_basic = "UPDATE " + str(tableName) + " SET " + str(key) + " = " + str(val) + " WHERE "
            for key_, val_ in cond.items():
                query_basic += str(key_) + " = " + str(val_) + " AND "
            query_basic = query_basic.strip(" AND ")
            query_basic += ";"
            query = text(query_basic)
            result = conn.execute(query)
        conn.commit()
        conn.close()
    engine.dispose()
    return 200


def patch_bulk_db(engineType, tableName, objList, condList):
    if engineType:
        engine = create_engine(deploy_uri)
    else:
        engine = create_engine(develop_uri)
    engine = engine.execution_options(autocommit=False)
    with engine.begin() as conn:
        for obj, cond in zip(objList, condList):
            for key, val in obj.items():
                query_basic = "UPDATE " + str(tableName) + " SET " + str(key) + " = " + str(val) + " WHERE "
                for key_, val_ in cond.items():
                    query_basic += str(key_) + " = " + str(val_) + " AND "
                query_basic = query_basic.strip(" AND ")
                query_basic += ";"
                query = text(query_basic)
                result = conn.execute(query)
        conn.commit()
        conn.close()
    engine.dispose()
    return 200


def patch_bulk_db2(engineType, tableName, objList, condList):
    if engineType:
        engine = create_engine(deploy_uri)
    else:
        engine = create_engine(develop_uri)
    engine = engine.execution_options(autocommit=False)
    with engine.begin() as conn:
        metadata = MetaData()
        table = Table(tableName, metadata, autoload_with=engine)
        stmt = update(table)

        bulkObj = []
        idx = 0 
        for obj, cond in zip(objList, condList):
            bulkObj_ = {}
            for key, val in cond.items():
                if idx == 0:
                    stmt = stmt.where(table.key==bindparam(key))
                bulkObj_[key] = val
            
            bindedObjList = {}
            for key, val in obj.items():
                bindedObjList[key] = bindparam("_"+key)
                bulkObj_["_"+key] = val

            bulkObj.append(bulkObj_)
            if idx == 0:
                stmt = stmt.values(bindedObjList)

            #print(210, stmt, bulkObj)
            idx += 1

        # print(stmt, bulkObj)
        conn.execute(stmt, bulkObj)
        conn.commit()
        conn.close()
    engine.dispose()
    return 200


def delete_bulk_db(engineType, tableName, condList):
    if engineType:
        engine = create_engine(deploy_uri)
    else:
        engine = create_engine(develop_uri)
    engine = engine.execution_options(autocommit=False)
    with engine.begin() as conn:
        for cond in condList:
            query_basic = "DELETE FROM " + str(tableName) + " WHERE "
            for key_, val_ in cond.items():
                query_basic += str(key_) + " = " + str(val_) + " AND "
            query_basic = query_basic.rstrip(" AND ")
            query_basic += ";"
            query = text(query_basic)
            result = conn.execute(query)
        conn.commit()
        conn.close()
    engine.dispose()
    return 200
import traceback
import akshare as ak
import pandas as pd
import concurrent.futures
import time
import re
import pymysql
import sys
from contextlib import contextmanager
import logging
from datetime import datetime
from job.job_factory import JobFactory
from service.workflow import WorkFlowApi
from worker import parse_args
from functools import partial

# 初始化logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 数据库连接管理器
@contextmanager
def db_connection(database='pnsql_workflow'):
    conn = None
    try:
        conn = pymysql.connect(
            host='8.153.100.186',
            port=3306,
            user='pengweiquan',
            password='PW1Q_.cn',
            database=database,
            charset='utf8mb4',
            autocommit=True
        )
        yield conn
    finally:
        if conn is not None:
            conn.close()

def get_code(symbol_fmt):
    m = re.search(r'(\d{6})$', symbol_fmt)
    if m:
        return m.group(1)
    else:
        return symbol_fmt

def fetch_and_insert_stock(args, logger):
    symbol, name, end_day, days = args
    symbol = str(symbol)
    if not symbol.isdigit() or len(symbol) != 6:
        logger.warning(f"{symbol} {name}: 非法股票代码，跳过")
        return

    for retry_cnt in range(3):
        try:
            # 股票前缀补全
            if symbol.startswith('6'):
                symbol_fmt = 'sh' + symbol
            elif symbol.startswith('4') or symbol.startswith('8'):
                symbol_fmt = 'bj' + symbol
            else:
                symbol_fmt = 'sz' + symbol

            df = ak.stock_zh_a_daily(symbol=symbol_fmt, adjust="qfq").reset_index()
            if df.empty:
                logger.info(f"{symbol} {name}: 无数据")
                return

            # 强制date列变为str，避免类型不一致
            df['date'] = df['date'].astype(str)
            df = df[df['date'] <= end_day]
            if df.empty:
                logger.info(f"{symbol} {name}: {end_day}及之前无数据")
                return

            df['symbol'] = get_code(symbol_fmt)
            df['name'] = name
            df['涨跌幅'] = (df['close'] - df['close'].shift(1)) / df['close'].shift(1) * 100
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA30'] = df['close'].rolling(window=30).mean()
            df['MA60'] = df['close'].rolling(window=60).mean()
            # 取最近N天数据，按日期逆序后head再正序
            insert_df = df[['symbol', 'date', 'open', 'close', 'high', 'low',
                            '涨跌幅', 'MA5', 'MA10', 'MA20', 'MA30', 'MA60', 'name']].sort_values(
                                    'date', ascending=False).head(days).sort_values('date')
            if insert_df.empty:
                logger.info(f"{symbol} {name}: 无可用数据，跳过")
                return
            insert_values = [
                (
                    row['symbol'],
                    row['date'],
                    float(row['open']),
                    float(row['close']),
                    float(row['high']),
                    float(row['low']),
                    float(row['涨跌幅']) if pd.notnull(row['涨跌幅']) else None,
                    float(row['MA5']) if pd.notnull(row['MA5']) else None,
                    float(row['MA10']) if pd.notnull(row['MA10']) else None,
                    float(row['MA20']) if pd.notnull(row['MA20']) else None,
                    float(row['MA30']) if pd.notnull(row['MA30']) else None,
                    float(row['MA60']) if pd.notnull(row['MA60']) else None,
                    row['name']
                )
                for idx, row in insert_df.iterrows()
            ]
            insert_query = """
            INSERT INTO p_stock
            (f0, f1, f2, f3, f4, f5, f9, f12, f13, f14, f15, f16, f20)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            with db_connection('pnsql_workflow') as conn:
                with conn.cursor() as cursor:
                    cursor.executemany(insert_query, insert_values)
            logger.info(f"{symbol} {name}: 入库成功({len(insert_values)}条)")
            logger.info(f"{symbol} {name}: 抓取并写入数据库完成")   # 新增日志
            break
        except Exception as e:
            logger.error(f"{symbol} {name} 抓取失败（第{retry_cnt+1}次），重试: {e}")
            time.sleep(2)
    else:
        logger.error(f"{symbol} {name} 多次失败跳过")
    return

if __name__ == "__main__":
    try:
        options = parse_args(sys.argv[1:])
        work = JobFactory(options.jobid)
        workflow = WorkFlowApi()
        work.logger.info("--------------------------------------任务开始-----------------------------------------------")
        # 自动用今天为end_day，抓最近600天
        end_day = datetime.now().strftime('%Y-%m-%d')
        days = 600
        work.logger.info(f"抓取截止日期: {end_day}，往前{days}天")

        # 清空主表
        with db_connection('pnsql_workflow') as conn:
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE p_stock")
            cursor.close()
        work.logger.info("p_stock表已清空")

        # 获取全部A股股票代码和名称
        df = ak.stock_zh_a_spot()
        df['symbol'] = df['代码'].astype(str).str.extract(r'(\d{6})$')
        spot_df = df[df['symbol'].notnull() & df['symbol'].str.isdigit()].copy()
        symbols = spot_df['symbol'].tolist()
        names = spot_df['名称'].tolist()
        argslist = [(s, n, end_day, days) for s, n in zip(symbols, names)]
        work.logger.info(f'共获取A股股票数: {len(symbols)}')

        # 多线程启动，每只股票抓取完都打印日志
        max_workers = 8
        fetch_func = partial(fetch_and_insert_stock, logger=work.logger)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(fetch_func, argslist))
        work.logger.info("全部A股入库完成")

        # ========== 全部入库后执行两个SQL ==========
        with db_connection('pnsql_workflow') as conn:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE p_follow_stock")
                cursor.execute("""
                    INSERT INTO p_follow_stock (stock_ticker,stock_name) 
                    SELECT DISTINCT f0,f20 FROM p_stock
                """)
        work.logger.info("p_follow_stock已更新")
        workflow.update_sub_task_data(options.jobid, "done")
    except Exception as e:
        work.logger.error(traceback.format_exc())


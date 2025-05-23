import sys
import traceback
import time
import akshare as ak
import pandas as pd
import pymysql
from contextlib import contextmanager
from job.job_factory import JobFactory
from service.workflow import WorkFlowApi
from worker import parse_args
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

def update_sql_with_date(conn, date_str):
    update_query = f"""
    UPDATE p_stock main
    SET
        f12 = (SELECT AVG(sub.f3) FROM (SELECT s.f3 FROM p_stock s WHERE s.f0 = main.f0 AND s.f1 <= '{date_str}' ORDER BY s.f1 DESC LIMIT 5) AS sub),
        f13 = (SELECT AVG(sub.f3) FROM (SELECT s.f3 FROM p_stock s WHERE s.f0 = main.f0 AND s.f1 <= '{date_str}' ORDER BY s.f1 DESC LIMIT 10) AS sub),
        f14 = (SELECT AVG(sub.f3) FROM (SELECT s.f3 FROM p_stock s WHERE s.f0 = main.f0 AND s.f1 <= '{date_str}' ORDER BY s.f1 DESC LIMIT 20) AS sub),
        f15 = (SELECT AVG(sub.f3) FROM (SELECT s.f3 FROM p_stock s WHERE s.f0 = main.f0 AND s.f1 <= '{date_str}' ORDER BY s.f1 DESC LIMIT 30) AS sub),
        f16 = (SELECT AVG(sub.f3) FROM (SELECT s.f3 FROM p_stock s WHERE s.f0 = main.f0 AND s.f1 <= '{date_str}' ORDER BY s.f1 DESC LIMIT 60) AS sub),
        f17 = (SELECT AVG(sub.f3) FROM (SELECT s.f3 FROM p_stock s WHERE s.f0 = main.f0 AND s.f1 <= '{date_str}' ORDER BY s.f1 DESC LIMIT 120) AS sub),
        f18 = (SELECT AVG(sub.f3) FROM (SELECT s.f3 FROM p_stock s WHERE s.f0 = main.f0 AND s.f1 <= '{date_str}' ORDER BY s.f1 DESC LIMIT 250) AS sub)
    WHERE main.f1 = '{date_str}';
    """
    with conn.cursor() as cursor:
        cursor.execute(update_query)
    print(f"均线批量更新完成：{date_str}")

def refresh_follow_stock(conn):
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE p_follow_stock;")
        cursor.execute("""
            INSERT INTO p_follow_stock (stock_ticker, stock_name)
            SELECT DISTINCT f0, f20 FROM p_stock;
        """)
    print("p_follow_stock 刷新完毕！")

def main():
    try:
        options = parse_args(sys.argv[1:])
        work = JobFactory(options.jobid)
        work.logger.info(
            "--------------------------------------任务开始-----------------------------------------------")
        workflow = WorkFlowApi()
        df = ak.stock_zh_a_spot()
        df_out = df[["代码", "名称", "最新价", "今开", "最高", "最低", "涨跌幅"]].copy()
        df_out = df_out.rename(columns={
            "代码": "symbol",
            "名称": "name",
            "最新价": "close",
            "今开": "open",
            "最高": "high",
            "最低": "low",
            "涨跌幅": "涨跌幅"
        })
        today_str = pd.Timestamp.now().strftime('%Y-%m-%d')
        df_out['date'] = today_str
        df_out['symbol'] = df_out['symbol'].astype(str).str.extract(r'(\d{6})$')

        replace_query = """
        REPLACE INTO p_stock
        (f0, f1, f2, f3, f4, f5, f9, f20)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        insert_values = [
            (
                row['symbol'],
                row['date'],
                float(row['open']) if pd.notnull(row['open']) else None,
                float(row['close']) if pd.notnull(row['close']) else None,
                float(row['high']) if pd.notnull(row['high']) else None,
                float(row['low']) if pd.notnull(row['low']) else None,
                float(row['涨跌幅']) if pd.notnull(row['涨跌幅']) else None,
                row['name']
            )
            for idx, row in df_out.iterrows()
            if pd.notnull(row['symbol']) and str(row['symbol']).isdigit()
        ]

        # 2. 限速写入数据库
        with db_connection('pnsql_workflow') as conn:
            with conn.cursor() as cursor:
                for v in insert_values:
                    cursor.execute(replace_query, v)
                    work.logger.info(f"已写入: symbol={v[0]}")
                    time.sleep(0.01)
            work.logger.info("全市场最新实时行情已自动覆盖/入库！")
            update_sql_with_date(conn, today_str)
            refresh_follow_stock(conn)
        workflow.update_sub_task_data(options.jobid, "done")
    except Exception as e:
        work.logger.error(traceback.format_exc())
if __name__ == "__main__":
    main()


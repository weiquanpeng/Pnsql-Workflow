import traceback
from urllib.parse import urlencode
import pandas as pd
import requests
import pymysql
from contextlib import contextmanager
import baostock as bs
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import time

from job.job_factory import JobFactory
from worker import parse_args

current_date = datetime.now()
formatted_current_date = current_date.strftime('%Y%m%d')
one_year_ago = current_date - timedelta(days=900)
formatted_one_year_ago = one_year_ago.strftime('%Y%m%d')

# 数据库连接管理器
@contextmanager
def db_connection(database='pnsql_workflow'):
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
    except Exception as e:
        work.logger.info(f"数据库连接失败: {e}")
        raise
    finally:
        conn.close()

# 获取股票代码和名称
def get_stock_codes(date=None):
    bs.login()
    stock_df = bs.query_all_stock(date).get_data()

    if len(stock_df) == 0:
        if date is not None:
            work.logger.info('当前选择日期为非交易日或尚无交易数据，请设置date为历史某交易日日期')
            sys.exit(0)

        delta = 1
        while len(stock_df) == 0:
            stock_df = bs.query_all_stock((datetime.now().date() - timedelta(days=delta)).strftime('%Y-%m-%d')).get_data()
            delta += 1

    bs.logout()
    stock_df = stock_df[(stock_df['code'] >= 'sh.600000') & (stock_df['code'] < 'sz.399000')]
    # 返回股票代码和名称的字典列表
    return stock_df[['code', 'code_name']].to_dict('records')

# 生成secid
def gen_secid(rawcode: str) -> str:
    if rawcode[:3] == '000' and len(rawcode) == 6:  # 修正：添加长度判断，避免误判沪市指数
        return f'0.{rawcode}'  # 000开头6位代码一般是深市股票
    if rawcode[:3] == '399':  # 深证指数
        return f'0.{rawcode}'
    if rawcode[0] != '6':  # 深市股票
        return f'0.{rawcode}'
    return f'1.{rawcode}'  # 沪市股票

# 获取K线数据
def get_k_history(code: str, beg: str, end: str, klt: int = 101, fqt: int = 1) -> list:
    EastmoneyKlines = {
        'f51': '日期',
        'f52': '开盘',
        'f53': '收盘',
        'f54': '最高',
        'f55': '最低',
        'f56': '成交量',
        'f57': '成交额',
        'f58': '振幅',
        'f59': '涨跌幅',
        'f60': '涨跌额',
        'f61': '换手率',
    }

    EastmoneyHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
    }

    fields = list(EastmoneyKlines.keys())
    columns = list(EastmoneyKlines.values())
    fields2 = ",".join(fields)
    secid = gen_secid(code)

    params = {
        'fields1': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13',
        'fields2': fields2,
        'beg': beg,
        'end': end,
        'rtntype': '6',
        'secid': secid,
        'klt': f'{klt}',
        'fqt': f'{fqt}',
    }

    base_url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'
    url = base_url + '?' + urlencode(params)

    try:
        response = requests.get(url, headers=EastmoneyHeaders)
        json_response = response.json()
        data = json_response.get('data')

        if data is None:
            secid = f'1.{code}' if secid[0] == '0' else f'0.{code}'
            params['secid'] = secid
            url = base_url + '?' + urlencode(params)
            response = requests.get(url, headers=EastmoneyHeaders)
            json_response = response.json()
            data = json_response.get('data')

        if data is None:
            work.logger.info(f'股票代码: {code} 可能有误，响应信息: {json_response}')
            return []

        klines = data['klines']
        rows = [kline.split(',') for kline in klines]
        return rows
    except Exception as e:
        work.logger.info(f'请求股票代码 {code} 数据时出现错误: {e}')
        return []

# 计算平均值
def hebing(p, y):
    averages = [0] * (y - 1)
    for i in range(len(p) - (y - 1)):
        subset = [float(x) for x in p[i:i + y]]
        average = round(sum(subset) / len(subset), 3)
        averages.append(format(average, '.3f'))
    return averages

# 处理股票数据并插入数据库
def p_start(stock_info):
    code = stock_info['code'].replace('.', '')[2:]  # 提取纯数字代码
    name = stock_info['code_name']  # 股票中文名称

    with db_connection('pnsql_workflow') as conn:
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        df = get_k_history(code, start_date, end_date)

        if not df:
            work.logger.info(f"股票 {code} 无数据或获取失败")
            return

        p_list = [i[2] for i in df]  # 收盘价
        p_list2 = [i[5] for i in df]  # 成交量

        # 计算各种平均值
        averages = {
            'x6': hebing(p_list, 5),
            'x18': hebing(p_list, 10),
            'x72': hebing(p_list, 20),
            'x96': hebing(p_list, 30),
            'x144': hebing(p_list, 60),
            'x200': hebing(p_list, 120),
            'x288': hebing(p_list, 250),
            'm6': hebing(p_list2, 5)
        }

        # 合并数据
        c_list = df
        for key, values in averages.items():
            c_list = [x + [y] for x, y in zip(c_list, values)]

        # 插入数据库（添加股票名称字段 f20）
        insert_query = """
        INSERT INTO p_stock (f0,f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        for i in c_list:
            cursor.execute(insert_query, (code,) + tuple(i) + (name,))

        work.logger.info(f"股票 {code} ({name}) 已获取完成")
        cursor.close()
        time.sleep(0.1)  # 添加适当的延迟

# 多线程执行
def execute_with_concurrency(stock_list, max_concurrent=5):
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        executor.map(p_start, stock_list)

if __name__ == "__main__":
    try:
        options = parse_args(sys.argv[1:])
        work = JobFactory(options.jobid)
        work.logger.info("--------------------------------------任务开始-----------------------------------------------")
        with db_connection('pnsql_workflow') as conn:
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE p_stock")
            cursor.close()
        work.logger.info("初始化表完成......")
        stock_infos = get_stock_codes()
        start_date = formatted_one_year_ago
        end_date = formatted_current_date
        execute_with_concurrency(stock_infos, max_concurrent=100)
        work.logger.info("股票代码获取完毕......")
    except Exception as e:
        work.logger.error(traceback.format_exc())
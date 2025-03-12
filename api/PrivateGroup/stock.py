from datetime import datetime, timedelta
import holidays
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from initialize.init_database import get_db
import util.response as response
from sqlalchemy.sql import text
from model.follow_stock import Follow_Stock
from model.stock import PwqScecss

router = APIRouter()

class StockRequest(BaseModel):
    f0Id: str = None

class DragonQueryRequest(BaseModel):
    date: str

# 构建返回信息
def build_stock_data(pwq_sce: PwqScecss):
    return {
        "id": pwq_sce.id,
        "f0": pwq_sce.f0,
        "f1": pwq_sce.f1.strftime("%Y-%m-%d") if pwq_sce.f1 else None,
        "f2": float(pwq_sce.f2),
        "f3": float(pwq_sce.f3),
        "f4": float(pwq_sce.f4),
        "f5": float(pwq_sce.f5),
        "f9": float(pwq_sce.f9),
        "f12": float(pwq_sce.f12),
        "f13": float(pwq_sce.f13),
        "f14": float(pwq_sce.f14),
        "f15": float(pwq_sce.f15),
        "f16": float(pwq_sce.f16),
        "f17": float(pwq_sce.f17),
        "f18": float(pwq_sce.f18)
    }

def get_previous_trading_day(date: datetime) -> datetime:
    cn_holidays = holidays.China()
    day_before = date - timedelta(days=1)
    while day_before.weekday() >= 5 or day_before in cn_holidays:
        day_before -= timedelta(days=1)
    return day_before

def serialize_follow_stock(stock):
    return {
        "stock_ticker": stock.stock_ticker,
        "follow": stock.follow,
        "stock_name": stock.stock_name
    }

async def execute_query_and_respond(session: AsyncSession, sql, params):
    try:
        f0_results = await PwqScecss.execute_raw_sql(session, sql, params)
        if not f0_results:
            return response.ok_with_message("没有找到符合条件的股票代码")
        follow_stocks = await Follow_Stock.get_follow_stocks_by_tickers(session, f0_results)
        if follow_stocks:
            serialized_data = [serialize_follow_stock(stock) for stock in follow_stocks]
            return response.ok_with_data({"data": serialized_data})
        else:
            return response.fail_with_message("没有找到符合条件的关注股票信息")
    except Exception as e:
        return response.fail_with_message(f"执行指定查询失败: {str(e)}")

@router.post("/stock_f0")
async def get_stock_by_f0(request: StockRequest, session: AsyncSession = Depends(get_db)):
    try:
        stocks = await PwqScecss.get_stock_by_f0(session, request.f0Id)
        if stocks:
            stock_list = [build_stock_data(i) for i in stocks]
            return response.ok_with_data({"data": stock_list})
        else:
            return response.fail_with_message("无对应股票代码")
    except Exception as e:
        return response.fail_with_message(f"查询对应股票信息失败！！！: {str(e)}")

@router.post("/sixty_moving_average")
async def execute_specific_sql_query(request: DragonQueryRequest, session: AsyncSession = Depends(get_db)):
    query_date = datetime.strptime(request.date, "%Y-%m-%d")
    y_date = get_previous_trading_day(query_date)
    start_date = query_date - timedelta(days=200)
    end_date = query_date - timedelta(days=10)

    sql = text("""
    SELECT DISTINCT f0
    FROM p_stock t1
    WHERE
        f1 = :y_date
        AND f3 < f16
        AND f0 IN (
            SELECT f0
            FROM p_stock
            WHERE f1 = :query_date AND f3 > f16
        )
        AND f0 NOT LIKE '30%'
        AND f0 NOT LIKE '68%'
        AND EXISTS (
            SELECT 1
            FROM p_stock AS t2
            WHERE t2.f0 = t1.f0
              AND t2.f1 BETWEEN :start_date AND :end_date
              AND t2.f9 > 9.5
        );
    """)
    params = {
        "query_date": request.date,
        "y_date": y_date.strftime("%Y-%m-%d"),
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    return await execute_query_and_respond(session, sql, params)


@router.post("/annual_moving_average")
async def annual_moving_average_query(request: DragonQueryRequest, session: AsyncSession = Depends(get_db)):
    query_date = datetime.strptime(request.date, "%Y-%m-%d")
    one_year_before_date = query_date - timedelta(days=365)
    prev_trading_day = get_previous_trading_day(query_date)
    two_days_before_prev_trading_day = get_previous_trading_day(prev_trading_day)

    # Construct the SQL query
    sql = text("""
    SELECT DISTINCT t1.f0
    FROM p_stock AS t1
    WHERE t1.f1 = :query_date
      AND t1.f3 - t1.f16 < t1.f3 * 0.05
      AND t1.f3 - t1.f16 > 0
      AND t1.f9 < 0
      AND t1.f0 NOT LIKE '30%'
      AND t1.f0 NOT LIKE '68%'
      AND EXISTS (
        SELECT 1
        FROM p_stock AS t2
        WHERE t2.f0 = t1.f0
          AND t2.f1 BETWEEN :one_year_before_date AND :query_date
          AND t2.f9 > 9.5
      )
      AND EXISTS (
        SELECT 1
        FROM p_stock AS t3
        WHERE t3.f0 = t1.f0
          AND t3.f1 = :prev_trading_day
          AND t3.f9 < 0
      )
      AND EXISTS (
        SELECT 1
        FROM p_stock AS t4
        WHERE t4.f0 = t1.f0
          AND t4.f1 = :two_days_before_prev_trading_day
          AND t4.f9 < 0
      );
    """)

    params = {
        "query_date": request.date,
        "one_year_before_date": one_year_before_date.strftime("%Y-%m-%d"),
        "prev_trading_day": prev_trading_day.strftime("%Y-%m-%d"),
        "two_days_before_prev_trading_day": two_days_before_prev_trading_day.strftime("%Y-%m-%d")
    }

    return await execute_query_and_respond(session, sql, params)


@router.post("/dragon_query")
async def sixty_moving_average_query(request: DragonQueryRequest, session: AsyncSession = Depends(get_db)):
    query_date = datetime.strptime(request.date, "%Y-%m-%d")
    sql = text("""
    SELECT DISTINCT f0 
    FROM p_stock 
    WHERE f1 = :query_date 
      AND f9 > 9.5 
      AND f0 NOT LIKE '30%' 
      AND f0 NOT LIKE '68%'
    """)
    params = {
        "query_date": request.date
    }
    return await execute_query_and_respond(session, sql, params)

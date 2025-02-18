from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from initialize.init_database import get_db
from model.follow_stock import Follow_Stock
import util.response as response
from model.follow_stock import Follow_Stock
router = APIRouter()

class UpdateFollowRequest(BaseModel):
    stock_ticker: str
    follow: int
# 构建返回信息
def build_stock_data(f_stock: Follow_Stock):
    return {
        "stock_ticker": f_stock.stock_ticker,
        "follow": f_stock.follow,
        "stock_name": f_stock.stock_name,
    }

@router.post("/FollowStock")
async def get_follow_stock_list(session: AsyncSession = Depends(get_db)):
    try:
        stocks = await Follow_Stock.get_follow_stock_list(session)
        if stocks:
            stock_list = [build_stock_data(i) for i in stocks]
            return response.ok_with_data({"data": stock_list})
        else:
            return response.fail_with_message("无关注股票代码")
    except Exception as e:
        return response.fail_with_message(f"查询关注股票信息失败！！！: {str(e)}")


@router.post("/UpdateFollow")
async def upt_follow_stock(request: UpdateFollowRequest, session: AsyncSession = Depends(get_db)):
    try:
        success = await Follow_Stock.update_follow_stock(session, request.stock_ticker, request.follow)
        if success:
            return response.ok_with_message("股票关注成功")
        else:
            return response.fail_with_message("股票关注失败")
    except Exception as e:
        return response.fail_with_message(f"股票关注失败{str(e)}")


@router.post("/FollowedList")
async def get_all_followed_stocks(session: AsyncSession = Depends(get_db)):
    try:
        # 调用模型中的方法获取所有 follow=1 的数据
        followed_stocks = await Follow_Stock.get_all_followed_stocks(session)
        stock_list = [build_stock_data(stock) for stock in followed_stocks]
        return response.ok_with_data({"data": stock_list})
    except Exception as e:
        # 捕获异常并返回错误信息
        return response.fail_with_message(f"获取关注股票出错: {str(e)}")
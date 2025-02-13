from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from initialize.init_database import get_db
from model.sys_user import SysUser
import util.response as response
from util.hashlib import hash_password
from datetime import datetime
from model.stock import PwqScecss



router = APIRouter()


class StockRequest(BaseModel):
    f0_id: str = None



# 构建返回信息
def build_stock_data(pwq_sce: PwqScecss):
    return {
       "id": pwq_sce.id,
        "f0": pwq_sce.f0,
        "f12": float(pwq_sce.f12),
        "f13": float(pwq_sce.f13),
        "f14": float(pwq_sce.f14),
        "f15": float(pwq_sce.f15),
        "f16": float(pwq_sce.f16),
        "f17": float(pwq_sce.f17)
    }



@router.post("/stock_f0")
async def get_stock_by_f0(request: StockRequest, session: AsyncSession = Depends(get_db)):
    try:
        stocks = await PwqScecss.get_stock_by_f0(session,request.f0_id)
        if stocks:
            stock_list = [build_stock_data(i) for i in stocks]
            return response.ok_with_data({"data": stock_list})
        else:
            return response.fail_with_message("无对应股票代码")
    except Exception as e:
        return response.fail_with_message(f"查询对应股票信息失败！！！: {str(e)}")

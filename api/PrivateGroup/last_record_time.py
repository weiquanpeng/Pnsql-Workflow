from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from initialize.init_database import get_db
from util.response import ok_with_data, fail_with_message, ok_with_message
from model.last_record_time import Last_Record_Time

router = APIRouter()

# 请求体模型，这里我们可以选择在更新时间时也传入日期
class RecordUpdateRequest(BaseModel):
    id: int
    dragon_time: str = None
    average_time: str = None
    gold_time: str = None

@router.post("/get_record_by_id")
async def get_record_by_id(session: AsyncSession = Depends(get_db)):
    try:
        # 默认使用 id 为 1
        default_id = 1
        records = await Last_Record_Time.get_all_records(session)
        for record in records:
            if record.id == default_id:
                return ok_with_data({
                    "id": record.id,
                    "dragon_time": record.dragon_time.strftime("%Y-%m-%d") if record.dragon_time else None,
                    "average_time": record.average_time.strftime("%Y-%m-%d") if record.average_time else None,
                    "gold_time": record.gold_time.strftime("%Y-%m-%d") if record.gold_time else None
                })
        return fail_with_message("查询收藏时间失败")
    except Exception as e:
        return fail_with_message(f"Error fetching record: {str(e)}")


@router.post("/update_dragon_time")
async def update_dragon_time(request: RecordUpdateRequest, session: AsyncSession = Depends(get_db)):
    print(request.dragon_time)
    try:
        dragon_time = datetime.strptime(request.dragon_time, "%Y-%m-%d").date()
        updated = await Last_Record_Time.update_dragon_time(session, request.id, dragon_time)
        if updated:
            return ok_with_message("更新收藏时间成功")
        else:
            return fail_with_message("更新收藏时间失败")
    except Exception as e:
        return fail_with_message(f"Error fetching record: {str(e)}")

@router.post("/update_average_time")
async def update_average_time(request: RecordUpdateRequest, session: AsyncSession = Depends(get_db)):
    try:
        average_time = datetime.strptime(request.average_time, "%Y-%m-%d").date()
        updated = await Last_Record_Time.update_average_time(session, request.id, average_time)
        if updated:
            return ok_with_message("更新收藏时间成功")
        else:
            return fail_with_message("更新收藏时间失败")
    except Exception as e:
        return fail_with_message(f"Error fetching record: {str(e)}")

@router.post("/update_gold_time")
async def update_gold_time(request: RecordUpdateRequest, session: AsyncSession = Depends(get_db)):
    try:
        gold_time = datetime.strptime(request.gold_time, "%Y-%m-%d").date()
        updated = await Last_Record_Time.update_gold_time(session, request.id, gold_time)
        if updated:
            return ok_with_message("更新收藏时间成功")
        else:
            return fail_with_message("更新收藏时间失败")
    except Exception as e:
        return fail_with_message(f"Error fetching record: {str(e)}")
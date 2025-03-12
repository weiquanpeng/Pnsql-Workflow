from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import util.response as response
from initialize.init_database import get_db
from model.subtask_config import SubTaskConfig
from model.task_config import TaskConfig
from sqlalchemy.exc import SQLAlchemyError

# 创建 FastAPI 路由器
router = APIRouter()

# 请求数据模型
class TaskRequest(BaseModel):
    id: int = None
    title: str = None
    owner: str = None
    approver: str = None
    status: str = None
    task_describe: str = None
    type: str = None
    paras: Dict[str, Any] = None
    created_time: datetime = None
    updated_time: datetime = None
    execute_time: datetime = None

# 构建用户数据字典
def build_user_data(task: SubTaskConfig):
    return {
        "id": task.id,
        "title": task.title,
        "owner": task.owner,
        "approver": task.approver,
        "status": task.status,
        "task_describe": task.task_describe,
        "type": task.type,
        "create_time": task.create_time.strftime("%Y-%m-%d %H:%M:%S") if task.create_time else None,
        "update_time": task.update_time.strftime("%Y-%m-%d %H:%M:%S") if task.update_time else None,
        "execute_time": task.execute_time.strftime("%Y-%m-%d %H:%M:%S") if task.execute_time else None
    }

@router.post("/TaskConfigGetMineList")
async def select_mine_user(request: TaskRequest, session: AsyncSession = Depends(get_db)):
    try:
        data = request.model_dump(exclude_unset=True)
        task_list = await TaskConfig.get_mine_task_list(session, data['owner'])
        task_data_list = [build_user_data(i) for i in task_list]
        return response.ok_with_data({"data": task_data_list})
    except Exception as e:
        return response.fail_with_message(f"查询我的工单出错: {str(e)}")

@router.post("/TaskConfigGetApproveList")
async def select_approve_list(request: TaskRequest, session: AsyncSession = Depends(get_db)):
    try:
        data = request.model_dump(exclude_unset=True)
        task_list = await TaskConfig.get_approve_task_list(session, data['approver'])
        task_data_list = [build_user_data(i) for i in task_list]
        return response.ok_with_data({"data": task_data_list})
    except Exception as e:
        return response.fail_with_message(f"查询我的审批出错: {str(e)}")


@router.post("/TaskConfigGetList")
async def select_list(session: AsyncSession = Depends(get_db)):
    try:
        task_list = await TaskConfig.get_task_list(session)
        task_data_list = [build_user_data(i) for i in task_list]
        return response.ok_with_data({"data": task_data_list})
    except Exception as e:
        return response.fail_with_message(f"查询所有工单出错: {str(e)}")


@router.post("/TaskConfigAddData")
async def insert_list(request: TaskRequest, session: AsyncSession = Depends(get_db)):
    try:
        data = request.model_dump(exclude_unset=True)
        new_data = await TaskConfig.insert_task(session, data)
        if new_data:
            new_data = build_user_data(new_data)
            return response.ok_with_data(new_data)
        else:
            return response.fail_with_message("创建工单失败")
    except SQLAlchemyError as e:
        return response.fail_with_message(f"数据库错误: {str(e)}")
    except Exception as e:
        return response.fail_with_message(f"创建工单出错: {str(e)}")

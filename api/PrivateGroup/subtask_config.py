from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import util.response as response
from initialize.init_database import get_db
from model.subtask_config import SubTaskConfig
from sqlalchemy.exc import SQLAlchemyError

from model.task_config import TaskConfig

# 创建 FastAPI 路由器
router = APIRouter()

# 请求数据模型
class SubtaskRequest(BaseModel):
    id: int = None
    status_id: int = None
    task_id: int = None
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
        "task_id": task.task_id,
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



@router.post("/SubTaskConfigList")
async def select_subtask_list(request: SubtaskRequest, session: AsyncSession = Depends(get_db)):
    try:
        task_id = request.task_id
        if task_id is None:
            return response.fail_with_message("task_id 不能为空")
        subtask_list = await SubTaskConfig.get_subtask_list(session, task_id)
        if subtask_list:
            subtask_data_list = [build_user_data(i) for i in subtask_list]
            return response.ok_with_data({"data": subtask_data_list})
        else:
            return response.ok_with_message("查询子任务失败或无结果")
    except SQLAlchemyError as e:
        return response.fail_with_message(f"数据库错误: {str(e)}")
    except Exception as e:
        return response.fail_with_message(f"查询子任务出错: {str(e)}")


@router.post("/UptSubTaskData")
async def update_subtask_status(
        request: SubtaskRequest,
        session: AsyncSession = Depends(get_db)
):
    try:
        if not request.id:
            return response.fail_with_message("ID 不能为空")
        if not request.status:
            return response.fail_with_message("Status 不能为空")

        # 更新子任务状态
        subtask_success = await SubTaskConfig.update_status_by_id(session, request.id, request.status)

        task_success = True
        if request.status in ["doing", "error", "close"]:
            task_id = await SubTaskConfig.get_task_id_by_id(session, request.id)
            task_success = await TaskConfig.update_task_status(session, task_id, request.status)
        elif request.status == "done":
            if hasattr(request, 'status_id') and request.status_id == 1:
                task_id = await SubTaskConfig.get_task_id_by_id(session, request.id)
                task_success = await TaskConfig.update_task_status(session, task_id, request.status)

        if not task_success:
            return response.fail_with_message("主任务状态更新失败")

        return response.ok_with_message("更新状态成功")

    except SQLAlchemyError as e:
        return response.fail_with_message(f"数据库错误: {str(e)}")
    except Exception as e:
        return response.fail_with_message(f"更新子任务状态出错: {str(e)}")


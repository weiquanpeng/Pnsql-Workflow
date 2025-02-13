from datetime import datetime
from fastapi import HTTPException, APIRouter, Depends, Query
import requests
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth
from sqlalchemy.ext.asyncio import AsyncSession
from initialize.init_config import config
import util.response as response
from initialize.init_database import get_db
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
    created_at: datetime = None
    updated_at: datetime = None
    execute_at: datetime = None

# 构建用户数据字典
def build_user_data(task: TaskConfig):
    return {
        "id": task.id,
        "title": task.title,
        "owner": task.owner,
        "approver": task.approver,
        "status": task.status,
        "task_describe": task.task_describe,
        "type": task.type,
        "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else None,
        "updated_at": task.updated_at.strftime("%Y-%m-%d %H:%M:%S") if task.updated_at else None,
        "execute_at": task.execute_at.strftime("%Y-%m-%d %H:%M:%S") if task.execute_at else None
    }

# 提取 Airflow API 配置和身份验证
def get_auth_and_base_url():
    auth = HTTPBasicAuth(config['airflow']['username'], config['airflow']['password'])
    base_url = config['airflow']['base_url']
    return auth, base_url

@router.post("/TaskConfigGetMineList")
async def select_user(request: TaskRequest, session: AsyncSession = Depends(get_db)):
    try:
        data = request.model_dump(exclude_unset=True)
        task_list = await TaskConfig.get_mine_task_list(session, data['owner'])
        if task_list:
            task_data_list = [build_user_data(i) for i in task_list]
            return response.ok_with_data({"data": task_data_list})
        else:
            return response.ok_with_message("查询我的工单失败")
    except Exception as e:
        return response.fail_with_message(f"查询我的工单出错: {str(e)}")

@router.post("/TaskConfigGetApproveList")
async def select_user(request: TaskRequest, session: AsyncSession = Depends(get_db)):
    try:
        data = request.model_dump(exclude_unset=True)
        task_list = await TaskConfig.get_approve_task_list(session, data['approver'])
        if task_list:
            task_data_list = [build_user_data(i) for i in task_list]
            return response.ok_with_data({"data": task_data_list})
        else:
            return response.fail_with_message("查询我的审批失败")
    except Exception as e:
        return response.fail_with_message(f"查询我的审批出错: {str(e)}")


@router.post("/TaskConfigGetList")
async def select_user(session: AsyncSession = Depends(get_db)):
    try:
        task_list = await TaskConfig.get_task_list(session)
        if task_list:
            task_data_list = [build_user_data(i) for i in task_list]
            return response.ok_with_data({"data": task_data_list})
        else:
            return response.ok_with_message("查询所有工单失败")
    except Exception as e:
        return response.fail_with_message(f"查询所有工单出错: {str(e)}")

# 创建工单
@router.post("/TaskConfigAddData")
async def insert_user(request: TaskRequest, session: AsyncSession = Depends(get_db)):
    async with session.begin():
        try:
            data = request.model_dump(exclude_unset=True)
            new_data = await TaskConfig.insert_task(session, data)
            if new_data:
                new_data = build_user_data(new_data)
                auth, base_url = get_auth_and_base_url()
                airflow_url = f"{base_url}/dags/{data['type']}/dagRuns"
                payload = {
                    "dag_run_id": str(new_data['id']),
                    "conf": {
                        "owner": new_data['owner']
                    }
                }
                try:
                    airflow_response = requests.post(
                        airflow_url, json=payload, auth=auth,
                        headers={'Content-Type': 'application/json'}
                    )
                    airflow_response.raise_for_status()
                except requests.RequestException as e:
                    await session.rollback()
                    raise HTTPException(status_code=500, detail=f"Error contacting Airflow API: {str(e)}")
                return response.ok_with_data(new_data)
            else:
                return response.fail_with_message("插入工单失败")
        except SQLAlchemyError as e:
            await session.rollback()
            return response.fail_with_message(f"数据库错误: {str(e)}")
        except Exception as e:
            await session.rollback()
            return response.fail_with_message(f"插入工单出错: {str(e)}")

# 查询主工单状态
# @router.get("/TaskConfigList")
# async def fetch_dag_run(dag_id: str, run_id: str):
#     auth, base_url = get_auth_and_base_url()
#     url = f"{base_url}/dags/{dag_id}/dagRuns/{run_id}"
#     try:
#         response_data = requests.get(url, auth=auth, headers={'Content-Type': 'application/json'})
#         if response_data.status_code == 200:
#             return response_data.json()
#         else:
#             raise HTTPException(status_code=response_data.status_code, detail="Failed to fetch data from Airflow API")
#     except requests.RequestException as e:
#         raise HTTPException(status_code=500, detail=str(e))

# 查询子工单状态
@router.post("/SubTaskConfigList")
async def fetch_task_instances(request: TaskRequest, dag_run_id: int = Query(..., description="The ID of the dag run")):
    task_type = request.type
    auth, base_url = get_auth_and_base_url()
    url = f"{base_url}/dags/{task_type}/dagRuns/{dag_run_id}/taskInstances"
    response_data = requests.get(url, auth=auth, headers={'Content-Type': 'application/json'})
    if response_data.status_code == 200:
        data = response_data.json()
        task_instances = data.get('task_instances', [])
        filtered_and_sorted_instances = sorted(
            [
                {
                    "task_id": task['task_id'],
                    "state": task['state'],
                    "start_date": task['start_date'],
                    "end_date": task['end_date'],
                    "try_number": task['try_number'],
                }
                for task in task_instances
            ],
            key=lambda x: x['start_date'] if x['start_date'] else ''
        )
        return response.ok_with_data({
            "task_instances": filtered_and_sorted_instances,
            "owner": "pengweiquan",
            "approver": "admin"
        })
    return response.fail_with_message(f"插入工单出错: {response_data.json()}")

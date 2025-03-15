from datetime import datetime
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base
import importlib
import os

from model.last_record_time import Last_Record_Time
from model.process_subtask_config import ProcessSubtaskConfig
from util.hashlib import hash_password


async def init_tables(engine: AsyncEngine, base: declarative_base, model_dir: str):
    # 导入 model 目录下的所有模块
    for root, _, files in os.walk(model_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = os.path.relpath(os.path.join(root, file), os.path.dirname(model_dir)).replace(os.sep, ".")[:-3]
                importlib.import_module(module_path)

    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

async def init_default_user(session: AsyncSession):
    from model.sys_user import SysUser
    result = await session.execute(select(SysUser).where(SysUser.account == "admin"))
    if result.scalars().first() is None:
        default_user = {
            "account": "admin",
            "password": hash_password("123123"),  # 加密密码
            "email": "admin@example.com",
            "roles": ["dba"],
            "phone": "12345678901",
            "enable": 1,  # 启用用户
        }
        new_user = SysUser(**default_user)
        session.add(new_user)
        await session.commit()

async def init_last_record_time(session: AsyncSession):
    today_date = datetime.now().date()
    result = await session.execute(select(Last_Record_Time).where(Last_Record_Time.id == 1))
    if result.scalars().first() is None:
        new_record = {
            "id": 1,
            "dragon_time": today_date,
            "average_time": today_date
        }
        stmt = insert(Last_Record_Time).values(new_record)
        await session.execute(stmt)
        await session.commit()

async def init_default_subtask_config(session: AsyncSession):
    # 定义要插入的记录
    default_subtask_configs = [
        {
            "name": "FabricStockExecution",
            "type": "job",
            "description": "全量爬虫任务",
            "exec_type": "bash",
            "script_host": "localhost",
            "interpreter": "python3",
            "script": "FabricStockExecution.py",
            "owner": "weiquanpeng"
        },
        {
            "name": "FollowStockExecution",
            "type": "job",
            "description": "增量爬虫任务",
            "exec_type": "bash",
            "script_host": "localhost",
            "interpreter": "python3",
            "script": "FollowStockExecution.py",
            "owner": "weiquanpeng"
        },
        {
            "name": "TaskDone",
            "type": "job",
            "description": "完成工单",
            "exec_type": "bash",
            "script_host": "localhost",
            "interpreter": "python3",
            "script": "TaskDone.py",
            "owner": "weiquanpeng"
        }
    ]
    for config in default_subtask_configs:
        result = await session.execute(
            select(ProcessSubtaskConfig).where(ProcessSubtaskConfig.name == config["name"])
        )
        if result.scalars().first() is None:
            new_subtask_config = ProcessSubtaskConfig(**config)
            session.add(new_subtask_config)
            await session.commit()
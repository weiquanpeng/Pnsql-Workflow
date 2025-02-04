from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base
import importlib
import os
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
    else:
        pass

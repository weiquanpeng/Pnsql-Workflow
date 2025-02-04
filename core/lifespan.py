import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from initialize.init_database import engine, get_db
from initialize.init_table import init_tables, init_default_user
from initialize.init_database import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # 初始化表结构
        model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
        await init_tables(engine, Base, model_dir)

        # 初始化默认用户
        async with AsyncSession(engine) as session:  # 手动创建 AsyncSession
            await init_default_user(session)
    except Exception as e:
        raise Exception(f"初始化失败: {e}")
    yield

app = FastAPI(lifespan=lifespan)
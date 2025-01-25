from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import declarative_base
import importlib
import os


async def init_tables(engine: AsyncEngine, base: declarative_base, model_dir: str):
    # 导入 model 目录下的所有模块
    for root, _, files in os.walk(model_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = os.path.relpath(os.path.join(root, file), os.path.dirname(model_dir)).replace(os.sep, ".")[:-3]
                importlib.import_module(module_path)

    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
from fastapi import FastAPI
import os
from importlib import import_module
from core.middleware import auth_middleware
from core.cors import setup_cors
from initialize.init_database import engine
from initialize.init_table import init_tables
from initialize.init_database import Base
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_dir = os.path.join(os.path.dirname(__file__), "model")
    await init_tables(engine, Base, model_dir)
    yield


app = FastAPI(
    title="PnSql Workflow",
    description="A FastAPI project with Workflow",
    version="2.0.0",
    lifespan=lifespan
)

# 添加全局中间件
app.middleware("http")(auth_middleware)

# 配置 CORS
setup_cors(app)

# 注册 PrivateGroup 路由
private_group_path = os.path.join(os.path.dirname(__file__), "routers", "PrivateGroup")
for module_name in os.listdir(private_group_path):
    if module_name.endswith(".py"):
        module = import_module(f"routers.PrivateGroup.{module_name[:-3]}")
        if hasattr(module, "router"):
            app.include_router(module.router, prefix="/api")

# 注册 PublicGroup 路由
public_group_path = os.path.join(os.path.dirname(__file__), "routers", "PublicGroup")
for module_name in os.listdir(public_group_path):
    if module_name.endswith(".py"):
        module = import_module(f"routers.PublicGroup.{module_name[:-3]}")
        if hasattr(module, "router"):
            app.include_router(module.router, prefix="/api/public")

# 打印所有注册的路由
def print_routes():
    print("----------------------------Registered Routes----------------------------")
    for route in app.routes:
        methods = ", ".join(route.methods) if hasattr(route, "methods") else "N/A"
        path = route.path if hasattr(route, "path") else "N/A"
        print(f"Path: {path}, Methods: {methods}")
    print("-------------------------------------------------------------------------")

# 在启动时打印路由
print_routes()
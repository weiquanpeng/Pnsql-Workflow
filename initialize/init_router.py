import os
from importlib import import_module
from fastapi import FastAPI

def print_routes(app: FastAPI):
    print("----------------------------Registered Routes----------------------------")
    for route in app.routes:
        methods = ", ".join(route.methods) if hasattr(route, "methods") else "N/A"
        path = route.path if hasattr(route, "path") else "N/A"
        print(f"Path: {path}, Methods: {methods}")
    print("-------------------------------------------------------------------------")

def init_routers(app: FastAPI):
    # 注册 PrivateGroup 路由
    private_group_path = os.path.join(os.path.dirname(__file__), "../api", "PrivateGroup")
    for module_name in os.listdir(private_group_path):
        if module_name.endswith(".py"):
            module = import_module(f"api.PrivateGroup.{module_name[:-3]}")
            if hasattr(module, "router"):
                app.include_router(module.router, prefix="/api")

    # 注册 PublicGroup 路由
    public_group_path = os.path.join(os.path.dirname(__file__), "../api", "PublicGroup")
    for module_name in os.listdir(public_group_path):
        if module_name.endswith(".py"):
            module = import_module(f"api.PublicGroup.{module_name[:-3]}")
            if hasattr(module, "router"):
                app.include_router(module.router, prefix="/api/public")

    # 打印所有注册的路由
    print_routes(app)

    return app
from fastapi import FastAPI
from core.middleware import auth_middleware
from core.cors import setup_cors
from core.lifespan import lifespan
from initialize.init_config import config
from initialize.init_router import init_routers

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

# 调用初始化路由函数
app = init_routers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config['app']['port'])
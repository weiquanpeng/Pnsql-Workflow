from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    """
    配置 CORS 中间件
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源，生产环境应改为具体的域名
        allow_credentials=True,  # 允许携带凭证（如 cookies）
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["*"],  # 允许所有 HTTP 头
    )

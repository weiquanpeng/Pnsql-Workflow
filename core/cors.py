from fastapi.middleware.cors import CORSMiddleware

from initialize.init_config import config


def setup_cors(app):
    origins=config['app']['file_path']
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 用具体的URL代替 *
        allow_credentials=True,  # 允许带凭证的请求
        allow_methods=["GET", "POST", "PUT"],  # 允许的方法
        allow_headers=["*"],  # 通常可以允许所有headers
    )
from fastapi import Request
from core.jwt import JWTUtils
from api.response.response import fail_with_data
from initialize.init_config import config
from initialize.init_database import AsyncSessionLocal
from model.jwt import JWT

# 定义你的永久token，可能从配置或环境变量中加载
PERMANENT_TOKEN = config['jwt']['permanent_token']


async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api") and not request.url.path.startswith("/api/public"):
        # 从请求头中获取 Token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return fail_with_data(801, {}, "未携带 Token")

        # 检查是否是永久token
        if auth_header == PERMANENT_TOKEN:
            # 如果是永久token，直接允许请求通过
            return await call_next(request)

        # 如果不是永久token，则继续正常的验证流程
        async with AsyncSessionLocal() as session:
            jwt_record = await JWT.get_jwt_by_token(session, auth_header)
            if jwt_record:
                return fail_with_data(801, {}, "Token 已加入黑名单")

            status_code = JWTUtils.verify_token(auth_header)
            if status_code == 1:
                pass
            elif status_code == 2:
                new_user = await JWT.insert_jwt(session, auth_header)
                return fail_with_data(801, {}, "Token 已过期")
            elif status_code == 3:
                return fail_with_data(801, {}, "Token 无效")

    response = await call_next(request)
    return response

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


async def auth_middleware(request: Request, call_next):
    # 如果路径以 /api 开头且不是 /api/public，则进行认证
    if request.url.path.startswith("/api") and not request.url.path.startswith("/api/public"):
        token = request.headers.get("Authorization")
        if not token or token != "valid_token":
            return JSONResponse(status_code=403, content={"detail": "Invalid token"})

    # 继续处理请求
    response = await call_next(request)
    return response
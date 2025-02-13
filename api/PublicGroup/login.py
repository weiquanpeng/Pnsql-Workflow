from datetime import timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.jwt import JWTUtils, ACCESS_TOKEN_EXPIRE_MINUTES
from initialize.init_database import get_db
from model.sys_user import SysUser
import util.response as response
from util.hashlib import verify_password


class UserRequest(BaseModel):
    id: int = None
    account: str = None
    email: str = None
    password: str = None
    roles: dict = None
    phone: str = None
    enable: int = 0


def build_user_data(user):
    return {
        "id": user.id,
        "account": user.account,
        "email": user.email,
        "roles": user.roles,
        "phone": user.phone,
        "enable": user.enable,
    }


router = APIRouter()


# 私有路由示例
@router.post("/login")
async def login(request: UserRequest, session: AsyncSession = Depends(get_db)):
    try:
        # 检查密码是否为空
        if not request.password:
            return response.fail_with_message("密码不能为空")

        # 根据账号查询用户
        user = await SysUser.get_user_by_account(session, request.account)
        if user:
            # 验证密码
            if verify_password(request.password, user.password):  # 假设用户模型的密码字段是 password
                # 生成 Token
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = JWTUtils.create_access_token(
                    data={"sub": user.account},  # 将用户账号编码到 Token 中
                    expires_delta=access_token_expires,
                )

                # 返回 Token 和用户信息
                user_data = build_user_data(user)
                return response.ok_with_data({
                    "access_token": access_token,
                    "user": user_data,
                })
            else:
                return response.fail_with_message("密码错误")
        else:
            return response.fail_with_message("用户不存在")
    except Exception as e:
        return response.fail_with_message(f"登录出错: {str(e)}")
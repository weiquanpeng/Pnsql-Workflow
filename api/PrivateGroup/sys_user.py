from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from initialize.init_database import get_db
from model.sys_user import SysUser
import util.response as response
from util.hashlib import hash_password

router = APIRouter()


class UserRequest(BaseModel):
    id: int = None
    account: str = None
    email: str = None
    password: str = None
    roles: list = None
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


@router.post("/SysGetUserList")
async def select_user(session: AsyncSession = Depends(get_db)):
    try:
        users = await SysUser.get_all_users(session)
        if users:
            user_data_list = [build_user_data(user) for user in users]
            return response.ok_with_data({"users": user_data_list})
        else:
            return response.ok_with_message("查询用户失败")
    except Exception as e:
        return response.fail_with_message(f"查询用户出错: {str(e)}")


@router.post("/SysAddUser")
async def insert_user(request: UserRequest, session: AsyncSession = Depends(get_db)):
    try:
        # 对密码进行哈希
        hashed_password = hash_password(request.password)
        # 更新请求数据中的密码字段
        data = request.model_dump(exclude_unset=True)
        data["password"] = hashed_password
        # 插入用户
        new_user = await SysUser.insert_user(session, data)
        if new_user:
            user_data = build_user_data(new_user)
            return response.ok_with_data(user_data)
        else:
            return response.fail_with_message("插入用户失败")
    except Exception as e:
        return response.fail_with_message(f"插入用户出错: {str(e)}")


@router.post("/SysUptUser")
async def update_user(request: UserRequest, session: AsyncSession = Depends(get_db)):
    try:
        if not request.id:
            return response.fail_with_message("用户ID不能为空")

        # 对密码进行哈希（如果提供了新密码）
        data = request.model_dump(exclude_unset=True)
        if "password" in data:
            data["password"] = hash_password(data["password"])

        # 更新用户
        updated_user = await SysUser.update_user(session, data)
        if updated_user:
            user_data = build_user_data(updated_user)
            return response.ok_with_data(user_data)
        else:
            return response.fail_with_message("更新用户失败")
    except Exception as e:
        return response.fail_with_message(f"更新用户出错: {str(e)}")


@router.post("/SysDelUser")
async def delete_user(request: UserRequest, session: AsyncSession = Depends(get_db)):
    try:
        user_id_to_delete = request.id
        # 插入用户
        success = await SysUser.delete_user(session, user_id_to_delete)
        if success:
            return response.ok()
        else:
            return response.fail_with_message("删除用户失败")
    except Exception as e:
        return response.fail_with_message(f"删除用户出错: {str(e)}")

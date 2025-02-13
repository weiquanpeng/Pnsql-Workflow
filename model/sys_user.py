from sqlalchemy import Column, BigInteger, DateTime, String, JSON, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from initialize.init_database import Base
from util.log import logger
logger = logger(__file__, log_level="INFO")

class SysUser(Base):
    __tablename__ = "sys_users"  # 数据库表名

    # 表字段
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    account = Column(String(128), index=True, comment="用户登录名")
    password = Column(String(128), comment="用户登录密码")
    roles = Column(JSON, comment="用户权限")
    phone = Column(String(128), comment="用户电话")
    email = Column(String(128), comment="用户邮箱")
    enable = Column(BigInteger, default=1, comment="用户是否被冻结 1正常 2冻结")

    @classmethod
    async def get_user_by_account(cls, session: AsyncSession, account: str):
        stmt = select(cls).where(cls.account == account).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_user_by_id(cls, session: AsyncSession, user_id: int):
        stmt = select(cls).where(cls.id == user_id).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all_users(cls, session: AsyncSession):
        stmt = select(cls).order_by(desc(cls.updated_at)).limit(1000)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def insert_user(cls, session: AsyncSession, data: dict):
        columns = cls.__table__.columns.keys()
        valid_data = {key: value for key, value in data.items() if key in columns}

        try:
            new_user = cls(**valid_data)
            session.add(new_user)
            await session.flush()  # 使用 await
            await session.refresh(new_user)  # 使用 await
            await session.commit()  # 使用 await
            logger.info("创建用户: {} 成功".format(new_user.account))
            return new_user
        except Exception as e:
            await session.rollback()  # 使用 await
            logger.error(f"插入用户失败，原因: {e}")
            return None

    @classmethod
    async def update_user(cls, session: AsyncSession, data: dict):
        columns = cls.__table__.columns.keys()
        valid_fields = ['id'] + [col for col in columns if col != 'id']
        valid_data = {field: data.get(field) for field in valid_fields if field in data}
        user_id = valid_data.pop('id', None)
        user = await cls.get_user_by_id(session, user_id)

        try:
            for key, value in valid_data.items():
                setattr(user, key, value)
            await session.commit()  # 使用 await
            logger.info(f"更新用户 ID {user_id} 成功")
            return user
        except Exception as e:
            await session.rollback()  # 使用 await
            logger.error(f"更新用户失败，原因: {e}")
            return None
    @classmethod
    async def delete_user(cls, session: AsyncSession, user_id: int):
        try:
            # 获取用户记录
            user = await cls.get_user_by_id(session, user_id)
            if user:
                # 删除用户
                await session.delete(user)
                await session.commit()  # 提交更改
                logger.info(f"删除用户 ID {user_id} 成功")
                return True
            else:
                logger.warning(f"用户 ID {user_id} 未找到")
                return False
        except Exception as e:
            await session.rollback()  # 回滚事务
            logger.error(f"删除用户失败，原因: {e}")
            return False
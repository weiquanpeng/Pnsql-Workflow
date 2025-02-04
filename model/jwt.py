from sqlalchemy import Column, BigInteger, DateTime, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from initialize.init_database import Base

class JWT(Base):
    __tablename__ = "jwt"  # 数据库表名

    # 表字段
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    jwt = Column(Text, comment="JWT 字符串")

    @classmethod
    async def get_jwt_by_token(cls, session: AsyncSession, token: str):
        stmt = select(cls).where(cls.jwt == token).limit(1)
        result = await session.execute(stmt)  # 使用 await
        return result.scalar_one_or_none()

    @classmethod
    async def insert_jwt(cls, session: AsyncSession, token: str):
        try:
            new_jwt = cls(jwt=token)  # 创建新记录
            session.add(new_jwt)  # 添加到会话
            await session.flush()  # 刷新会话以生成 ID
            await session.refresh(new_jwt)  # 刷新记录以获取数据库默认值
            await session.commit()  # 提交事务
            return new_jwt
        except Exception as e:
            await session.rollback()  # 回滚事务
            return None

from sqlalchemy import Column, BigInteger, DateTime, String, JSON, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from initialize.init_database import Base
from util.log import logger
logger = logger(__file__, log_level="INFO")
class TaskConfig(Base):
    __tablename__ = "task_config"  # 数据库表名
    # 表字段
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    title = Column(String(64), nullable=True, comment="任务名")
    owner = Column(String(64), nullable=True, comment="提交人")
    approver = Column(String(64), nullable=True, comment="审批人")
    status = Column(String(32), nullable=True, index=True, comment="工单状态")
    task_describe = Column(String(128), nullable=True, comment="工单描述")
    type = Column(String(32), nullable=True, index=True, comment="任务函数名")
    execute_at = Column(DateTime, nullable=True, comment="定时执行时间")

    # 表级选项
    __table_args__ = (
        {"comment": "任务配置表"},
    )

    @classmethod
    async def get_mine_task_list(cls, session: AsyncSession, user: str):
        stmt = (select(cls).where(cls.owner == user).order_by(desc(cls.updated_at)).limit(1000))
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_approve_task_list(cls, session: AsyncSession, user: str):
        stmt = (select(cls).where(cls.approver == user).order_by(desc(cls.updated_at)).limit(1000))
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_task_list(cls, session: AsyncSession):
        stmt = select(cls).order_by(desc(cls.updated_at)).limit(1000)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def insert_task(cls, session: AsyncSession, data: dict):
        columns = cls.__table__.columns.keys()
        valid_data = {key: value for key, value in data.items() if key in columns}
        try:
            new_user = cls(**valid_data)
            session.add(new_user)
            await session.flush()  # 使用 await
            await session.refresh(new_user)  # 使用 await
            await session.commit()  # 使用 await
            logger.info("创建工单: {} 成功".format(new_user. id))
            return new_user
        except Exception as e:
            await session.rollback()  # 使用 await
            logger.error(f"创建工单失败，原因: {e}")
            return None


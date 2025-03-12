from sqlalchemy import Column, BigInteger, DateTime, String, JSON, select, desc, text, update, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from initialize.init_database import Base
from model.subtask_config import SubTaskConfig


class TaskConfig(Base):
    __tablename__ = "task_config"  # 数据库表名
    # 表字段
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    create_time = Column(DateTime,nullable=False,server_default=text("CURRENT_TIMESTAMP"),comment="创建时间")
    update_time = Column(DateTime,nullable=False,server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),comment="更新时间")
    title = Column(String(64), nullable=True, comment="任务名")
    owner = Column(String(64), nullable=True, comment="提交人")
    approver = Column(String(64), nullable=True, comment="审批人")
    status = Column(String(32), nullable=True, index=True, comment="工单状态")
    task_describe = Column(String(128), nullable=True, comment="工单描述")
    type = Column(String(64), nullable=True, index=True, comment="任务函数名")
    paras = Column(JSON, nullable=True, comment="任务参数")
    execute_time = Column(DateTime, nullable=True, comment="定时执行时间")

    # 表级选项
    __table_args__ = (
        {"comment": "任务配置表"},
    )

    @classmethod
    async def get_mine_task_list(cls, session: AsyncSession, user: str):
        stmt = (select(cls).where(cls.owner == user).where(cls.status != 'close').order_by(desc(cls.update_time)).limit(1000))
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_approve_task_list(cls, session: AsyncSession, user: str):
        # 创建两个表之间的联立查询
        stmt = (
            select(cls)
            .join(SubTaskConfig, cls.id == SubTaskConfig.task_id)
            .where(cls.status != 'close')
            .where(and_(
                SubTaskConfig.status == 'todo',
                SubTaskConfig.approver == user
            ))
            .order_by(desc(cls.update_time))
            .limit(1000)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_task_list(cls, session: AsyncSession):
        stmt = select(cls).order_by(desc(cls.update_time)).limit(1000)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def insert_task(cls, session: AsyncSession, data: dict):
        columns = cls.__table__.columns.keys()
        valid_data = {key: value for key, value in data.items() if key in columns}
        try:
            new_user = cls(**valid_data)
            session.add(new_user)
            await session.flush()
            await session.refresh(new_user)
            await session.commit()
            return new_user
        except Exception as e:
            await session.rollback()
            return None

    @classmethod
    async def update_task_status(cls, session: AsyncSession, task_id: int, new_status: str):
        try:
            # 构建更新语句
            stmt = (update(cls).where(cls.id == task_id).values(status=new_status))
            await session.execute(stmt)
            await session.commit()
            updated_task = await session.get(cls, task_id)
            return updated_task
        except SQLAlchemyError as e:
            await session.rollback()
            print(f"更新任务状态失败: {e}")
            return None
from sqlalchemy import Column, BigInteger, DateTime, String, JSON, text, desc, select, asc, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from initialize.init_database import Base

class SubTaskConfig(Base):
    __tablename__ = "subtask_config"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    create_time = Column(DateTime,nullable=False,server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_time = Column(DateTime,nullable=False,server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),comment="更新时间")
    title = Column(String(64), nullable=True, comment="任务名")
    owner = Column(String(64), nullable=True, index=True, comment="提交人")
    approver = Column(String(64), nullable=True, comment="审批人")
    task_id = Column(BigInteger, nullable=False, index=True, comment="主任务ID")
    status = Column(String(32), nullable=True, index=True, comment="工单状态")
    paras = Column(JSON, nullable=True, comment="任务参数")
    type = Column(String(64), nullable=True, index=True, comment="子任务函数")
    task_describe = Column(String(128), nullable=True, comment="工单描述")
    execute_time = Column(DateTime, nullable=True, default=None, comment="执行时间")

    __table_args__ = (
        {"comment": "子任务配置表"},
    )

    @classmethod
    async def get_task_id_by_id(cls, session: AsyncSession, subtask_id: int):
        try:
            stmt = select(cls.task_id).where(cls.id == subtask_id)
            result = await session.execute(stmt)
            subtask = result.scalar_one_or_none()
            return subtask
        except SQLAlchemyError:
            return None
    @classmethod
    async def get_subtask_list(cls, session: AsyncSession, task_id: int):
        stmt = select(cls).where(cls.task_id == task_id).order_by(asc(cls.id))
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update_status_by_id(cls, session: AsyncSession, subtask_id: int, new_status: str):
        stmt = (update(cls).where(cls.id == subtask_id).values(status=new_status).execution_options(synchronize_session="fetch"))
        result = await session.execute(stmt)
        await session.commit()
        if result.rowcount > 0:
            return True
        else:
            return False
from sqlalchemy import Column, BigInteger, update, select, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from initialize.init_database import Base

class Last_Record_Time(Base):
    __tablename__ = "last_record_time"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    dragon_time = Column(Date, nullable=True, comment="龙回头上次记录时间")
    average_time = Column(Date, nullable=True, comment="均线上次记录时间")
    gold_time = Column(Date, nullable=True, comment="黄金线上次记录时间")

    __table_args__ = (
        {"comment": "时间记录表"},
    )

    @classmethod
    async def get_all_records(cls, session: AsyncSession):
        """读取所有记录"""
        try:
            stmt = select(cls)
            result = await session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            print(f"Error fetching all records: {e}")
            return None


    @classmethod
    async def update_dragon_time(cls, session: AsyncSession, record_id: int, dragon_time):
        """更新指定记录的 dragon_time 字段值"""
        try:
            stmt = (
                update(cls)
                .where(cls.id == record_id)
                .values(dragon_time=dragon_time)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Error updating dragon_time: {e}")
            return False

    @classmethod
    async def update_average_time(cls, session: AsyncSession, record_id: int, average_time):
        """更新指定记录的 average_time 字段值"""
        try:
            stmt = (
                update(cls)
                .where(cls.id == record_id)
                .values(average_time=average_time)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Error updating average_time: {e}")
            return False

    @classmethod
    async def update_gold_time(cls, session: AsyncSession, record_id: int, gold_time):
        """更新指定记录的 average_time 字段值"""
        try:
            stmt = (
                update(cls)
                .where(cls.id == record_id)
                .values(gold_time=gold_time)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Error updating average_time: {e}")
            return False
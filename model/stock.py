from sqlalchemy import Column, Date, String, BigInteger, Integer, DECIMAL, Index, UniqueConstraint
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from initialize.init_database import Base
from typing import List, Dict, Any

class PwqScecss(Base):
    __tablename__ = 'p_stock'  # 数据库表名

    # 表字段
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='ID')
    f0 = Column(String(20), comment='股票代码')
    f1 = Column(Date, comment='日期')
    f2 = Column(DECIMAL(20, 3), comment='开盘')
    f3 = Column(DECIMAL(20, 3), comment='收盘')
    f4 = Column(DECIMAL(20, 3), comment='最高')
    f5 = Column(DECIMAL(20, 3), comment='最低')
    f6 = Column(Integer, comment='成交量')
    f7 = Column(BigInteger, comment='成交额')
    f8 = Column(DECIMAL(20, 3), comment='振幅')
    f9 = Column(DECIMAL(20, 3), comment='涨跌幅')
    f10 = Column(DECIMAL(20, 3), comment='涨跌额')
    f11 = Column(DECIMAL(20, 3), comment='换手率')
    f12 = Column(DECIMAL(20, 3), comment='k-5')
    f13 = Column(DECIMAL(20, 3), comment='k-10')
    f14 = Column(DECIMAL(20, 3), comment='k-20')
    f15 = Column(DECIMAL(20, 3), comment='k-30')
    f16 = Column(DECIMAL(20, 3), comment='k-60')
    f17 = Column(DECIMAL(20, 3), comment='k-120')
    f18 = Column(DECIMAL(20, 3), comment='k-250')
    f19 = Column(DECIMAL(20, 3), comment='成交量均值')
    f20 = Column(String(30), comment='股票名称')

    # 索引
    __table_args__ = (
        UniqueConstraint('f0', 'f1', name='uq_stock_date'),
        Index('in_1', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19'),
        Index('in_2', 'f1'),
        Index('in_3', 'f6'),
        Index('in_4', 'f0'),
    )

    @classmethod
    async def get_stock_by_f0(cls, session: AsyncSession, f0_id: str):
        stmt = select(cls).where(cls.f0 == f0_id).order_by(cls.f1.asc())
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def execute_raw_sql(cls, session: AsyncSession, sql: str, params: dict = {}) -> List[Any]:
        try:
            result = await session.execute(sql, params)
            rows = result.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            return []
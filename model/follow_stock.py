from typing import List
from sqlalchemy import Column, String, BigInteger, Integer, Index, update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from initialize.init_database import Base

class Follow_Stock(Base):
    __tablename__ = 'p_follow_stock'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='ID')
    stock_ticker = Column(String(20), comment='股票代码')
    follow = Column(Integer, server_default='0', comment='是否关注')
    stock_name = Column(String(20), comment='股票名称')

    # 索引
    __table_args__ = (
        Index('in_stock_ticker', 'stock_ticker'),
    )

    @classmethod
    async def get_follow_stock_list(cls, session: AsyncSession):
        stmt = select(cls).order_by(cls.stock_ticker.asc())
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update_follow_stock(cls, session: AsyncSession, ticker: str, status: int):
        stmt = (
            update(cls)
            .where(cls.stock_ticker == ticker)
            .values(follow=status)
            .execution_options(synchronize_session="fetch")
        )
        try:
            await session.execute(stmt)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            return False

    @classmethod
    async def get_follow_stocks_by_tickers(cls, session: AsyncSession, tickers: List[str]):
        stmt = select(cls).where(cls.stock_ticker.in_(tickers)).order_by(cls.stock_ticker.asc())
        try:
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            return []

    @classmethod
    async def get_all_followed_stocks(cls, session: AsyncSession):
        stmt = select(cls).where(cls.follow == 1).order_by(cls.stock_ticker.asc())
        try:
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            return []

    @classmethod
    async def reset_all_follow_fields(cls, session: AsyncSession):
        stmt = (
            update(cls)
            .values(follow=0)
            .execution_options(synchronize_session="fetch")
        )
        try:
            await session.execute(stmt)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            return False
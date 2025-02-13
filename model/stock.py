from sqlalchemy import Column, Date, String, BigInteger, Integer, DECIMAL, Index
from initialize.init_database import Base

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
    f17 = Column(DECIMAL(20, 3), comment='k-250')
    f18 = Column(DECIMAL(20, 3), comment='成交量均值')

    # 索引
    __table_args__ = (
        Index('in_1', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18'),
        Index('in_2', 'f1'),
        Index('in_3', 'f6'),
        Index('in_4', 'f0'),
    )

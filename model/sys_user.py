from sqlalchemy import Column, BigInteger, DateTime, String, JSON
from sqlalchemy.sql import func
from initialize.init_database import Base

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
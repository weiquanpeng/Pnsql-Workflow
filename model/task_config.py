from sqlalchemy import Column, BigInteger, DateTime, String, JSON
from sqlalchemy.sql import func
from initialize.init_database import Base

class TaskConfig(Base):
    __tablename__ = "task_config"  # 数据库表名

    # 表字段
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    title = Column(String(128), nullable=True, comment="任务名")
    owner = Column(String(128), nullable=True, comment="提交人")
    status = Column(String(128), nullable=True, index=True, comment="工单状态")  # Indexed column
    parameter = Column(JSON, nullable=True, comment="配置参数")
    task_describe = Column(String(128), nullable=True, comment="工单描述")
    type = Column(String(128), nullable=True, index=True, comment="任务函数名")  # Indexed column
    account = Column(String(128), index=True, comment="用户登录名")  # New indexed column

    # 表级选项
    __table_args__ = (
        {"comment": "任务配置表"},
    )

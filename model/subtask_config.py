from sqlalchemy import Column, BigInteger, DateTime, String, JSON, ForeignKey
from sqlalchemy.sql import func
from initialize.init_database import Base

class SubtaskConfig(Base):
    __tablename__ = "subtask_config"  # 数据库表名

    # 表字段
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    title = Column(String(128), nullable=True, comment="任务名")
    type = Column(String(128), nullable=True, index=True, comment="任务函数名")  # Indexed column
    owner = Column(String(128), nullable=True, index=True, comment="提交人")  # Indexed column
    approve = Column(String(128), nullable=True, comment="审批人")
    task_id = Column(BigInteger, ForeignKey("task_config.id"), nullable=True, index=True, comment="主任务ID")  # Indexed column
    status = Column(String(128), nullable=True, index=True, comment="工单状态")  # Indexed column
    parameter = Column(JSON, nullable=True, comment="配置参数")
    task_describe = Column(String(128), nullable=True, comment="工单描述")
    account = Column(String(128), index=True, comment="用户登录名")  # New indexed column

    # 表级选项
    __table_args__ = (
        {"comment": "子任务配置表"},
    )

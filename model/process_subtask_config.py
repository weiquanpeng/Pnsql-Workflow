from sqlalchemy import Column, BigInteger, DateTime, String, text
from initialize.init_database import Base



class ProcessSubtaskConfig(Base):
    __tablename__ = "process_subtask_config"  # 表名

    # 表字段
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键 ID")
    name = Column(String(64), nullable=False, unique=True, comment="任务名")
    type = Column(String(64), nullable=False, server_default=text("'job'"), comment="子任务类型: job, cronjob")
    description = Column(String(255), nullable=False, server_default=text("''"), comment="描述")
    exec_type = Column(String(64), nullable=False, server_default=text("'bash'"), comment="操作类型: bash, ssh")
    script_host = Column(String(64), nullable=False, server_default=text("'localhost'"), comment="脚本所在机器: localhost, ip")
    interpreter = Column(String(64), nullable=False, server_default=text("'python3'"), comment="解释器: python3, bash")
    script = Column(String(128), nullable=False, server_default=text("''"), comment="脚本路径")
    owner = Column(String(64), nullable=False, server_default=text("'sikui'"), comment="owner")
    createtime = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")
    updatetime = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")

    # 表级选项
    __table_args__ = (
        {"comment": "子任务配置表"},
    )


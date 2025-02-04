from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from initialize.init_config import config

# 数据库连接配置
DATABASE_URL = (
    f"mysql+aiomysql://{config['database']['username']}:{config['database']['password']}@"
    f"{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
)

# 创建异步数据库引擎，并详细配置连接池
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 打印 SQL 语句（调试用）
    pool_size=5,  # 连接池的初始大小
    max_overflow=100,  # 连接池允许的最大溢出连接数
    pool_timeout=10,  # 连接池获取连接的超时时间（秒）
    pool_recycle=3600,  # 连接池回收时间
)

# 创建异步会话工厂，开启自动提交模式
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 声明基类
Base = declarative_base()

# 获取数据库会话的依赖函数
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
from initialize.init_config import config
import logging
from datetime import datetime
import os  # 引入 os 模块

def logger(log_name='pnsql-workflow', log_level='INFO'):
    # 检查 log_level 是否有效
    if log_level and log_level.upper() not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        raise ValueError("log_level must be one of ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')")

    # 提取 log_name 中的文件名部分
    log_name = os.path.basename(log_name)  # 获取路径中的文件名

    # 日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 日志文件路径
    log_file = '{}/{}.{}'.format(config["app"]["log_path"], log_name, datetime.today().strftime('%Y%m%d'))

    # 文件处理器
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    # 创建日志记录器
    logger = logging.getLogger(log_name)
    logger.setLevel(log_level.upper())  # 设置日志级别
    logger.addHandler(handler)

    return logger
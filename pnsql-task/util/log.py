import logging
import os
from datetime import datetime
from conf.config import config


def logger(log_number=None):
    # 固定的日志名称和日志级别
    log_name = 'pnsql-task'
    log_level = 'INFO'

    # 提取 log_name 中的文件名部分
    log_name = os.path.basename(log_name)  # 获取路径中的文件名

    # 日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 如果提供了日志编号，则使用该编号创建特定格式的日志文件，否则使用时间戳
    if log_number is not None:
        log_file = '{}/{}.log'.format(config["app"]["log_path"], log_number)
        logger_name = f"{log_name}_{log_number}"
    else:
        log_file = '{}/{}.{}.log'.format(config["app"]["log_path"], log_name, datetime.today().strftime('%Y%m%d'))
        logger_name = log_name

    # 创建并检查日志记录器是否已经存在，避免重复添加处理器
    logger = logging.getLogger(logger_name)
    if not logger.handlers:  # 仅在没有处理器的情况下添加，防止重复日志条目
        # 文件处理器
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)

        # 设置日志级别并添加处理器
        logger.setLevel(log_level)
        logger.addHandler(handler)

    return logger

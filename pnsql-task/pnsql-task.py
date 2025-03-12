# -*- coding: utf-8 -*-
import time
import traceback
from scheduler import Scheduler
from util.log import logger
logger=logger()

if __name__ == "__main__":
    try:
        scheduler = Scheduler()
        scheduler.run()
    except Exception as e:
        errmsg = "pnsql-task 状态异常! <{}>".format(traceback.format_exc())
        logger.error(errmsg)

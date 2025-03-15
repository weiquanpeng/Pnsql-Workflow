# -*- coding: utf-8 -*-
import json
import traceback

from conf.config import config
from job_command import JobCommand
from model.taskdb import TaskDB
from util.command import safe_execute_local_cmd
from util.log import logger
from worker import parse_args

class JobFactory(object):
    def __init__(self, jobid):
        conn_setting = dict(config['database'])
        self.db = TaskDB(conn_setting)
        self.job = self.db.get_subtask_by_id(jobid)
        self.job['paras'] = json.loads(self.job['paras'])
        self.logger = logger(self.job['task_id'])

    def run(self):
        command = JobCommand(self.db.get_subtask_config(self.job['type']), self.job)
        self.logger.info(command.command)
        try:
            stdout = safe_execute_local_cmd(command.command)
            self.logger.info(stdout)
        except Exception as e:
            self.logger.error(traceback.format_exc())
import json
from util.log import logger
class TaskFactory(object):
    def __init__(self, task):
        self.task = task
        if isinstance(task['paras'], str):
            self.task['paras'] = json.loads(task['paras'])
        self.subtasks = [
            {
                'taskid': self.task['id'],
                'title': '提交工单',
                'owner': self.task['owner'],
                'approver': self.task['owner'],
                'status': 'done',
                'paras': self.task['paras'],
                'task_describe': self.task['task_describe'],
                'type': '',
            },
        ]
        self.logger = logger(self.task['id'])
        self.logger.info(f"工单 {self.task['id']} 初始化...")
    def finalize_task(self):
        """在每个子类创建子任务之后调用此方法以添加“工单完成”任务"""
        self.subtasks.append({
            'taskid': self.task['id'],
            'title': '工单完成',
            'owner': 'system',
            'approver': '',
            'status': 'tosplit',
            'paras': '',
            'task_describe': self.task['task_describe'],
            'type': 'TaskDone',
        })
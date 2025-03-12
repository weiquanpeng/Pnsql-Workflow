import json

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
                'task_describe': '工单提交完毕',
                'type': '',
            },
        ]
    def finalize_task(self):
        """在每个子类创建子任务之后调用此方法以添加“工单完成”任务"""
        self.subtasks.append({
            'taskid': self.task['id'],
            'title': '工单完成',
            'owner': 'system',
            'approver': '',
            'status': 'tosplit',
            'paras': '',
            'task_describe': '工单已完成',
            'type': 'TaskDone',
        })
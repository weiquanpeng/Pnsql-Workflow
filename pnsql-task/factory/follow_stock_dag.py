from factory.task_factory import TaskFactory

class FollowStockDag(TaskFactory):
    def create_subtasks(self):
        # 创建并添加每个子任务
        self.add_owner_approve_subtask()
        self.add_leader_approve_subtask()
        self.add_execution_task()
        self.finalize_task()
    # 添加 "owner 审批" 子任务
    def add_owner_approve_subtask(self):
        subtask = {
            'taskid': self.task['id'],
            'title': 'owner 审批',
            'owner': self.task['owner'],
            'approver': self.task['owner'],
            'status': 'tosplit',
            'paras': self.task['paras'],
            'task_describe': '这是一个增量任务',
            'type': 'OwnerApproveSubtask',
        }
        self.subtasks.append(subtask)

    # 添加 "leader 审批" 子任务
    def add_leader_approve_subtask(self):
        subtask = {
            'taskid': self.task['id'],
            'title': 'leader 审批',
            'owner': 'admin',
            'approver': 'wanguangqiu,sikui',
            'status': 'tosplit',
            'paras': self.task['paras'],
            'task_describe': '这是一个增量任务',
            'type': 'LeaderApproveSubtask',
        }
        self.subtasks.append(subtask)

    # 添加 "任务执行" 子任务
    def add_execution_task(self):
        subtask = {
            'taskid': self.task['id'],
            'title': '任务执行',
            'owner': 'system',
            'approver': '',
            'status': 'tosplit',
            'paras': self.task['paras'],
            'task_describe': '这是一个增量任务',
            'type': 'FollowStockExecution',
        }
        self.subtasks.append(subtask)

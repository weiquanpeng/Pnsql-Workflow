import requests
from conf.config import config

class WorkFlowApi:
    def __init__(self):
        self.baseurl = config['app']['baseurl']
        self.headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json',
            'Authorization': 'ekJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczODMyNDQ5OH0.9znJOAPKjmRuoSQwTM0GIZYfS8FbUhGjXvA7ZVvkZkW',
        }

    def update_sub_task_data(self, task_id, status, status_id=0):
        url = f"{self.baseurl}/api/UptSubTaskData"
        data = {
            'id': task_id,
            'status': status,
            'status_id': status_id  # 添加对 status_id 的支持
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

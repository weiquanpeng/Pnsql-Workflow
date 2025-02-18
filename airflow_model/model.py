from airflow.models import Variable

def setup_variables(run_id, task_types=None):
    if task_types is None:
        print(f"{run_id} 生成工单")
    else:
        for task_type in task_types:
            Variable.set(f"{task_type}_{run_id}", "False")

def done_for_task(run_id):
    """工单完成"""
    print("{run_id} 工单完成")

def check_approval(task_id, run_id):
    approved_var = f"{task_id}_{run_id}"
    return Variable.get(approved_var, default_var="False") == "True"
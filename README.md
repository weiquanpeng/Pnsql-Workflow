```
vi ~/.bash_profile
---------------------------------------------------------
export PYTHONPATH=/data/Pnsql-Workflow/pnsql-task
---------------------------------------------------------
```

```
## Pnsql_Workflow
cd /data/Pnsql-Workflow
/usr/local/python3/bin/python3 -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt
nohup .venv/bin/python main.py &
```

```
## Pnsql_Task
cd /data/Pnsql-Workflow/pnsql-task
mkdir -p log
/usr/local/python3/bin/python3 -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt
nohup .venv/bin/python pnsql-task.py &
```

from factory.fabric_stock_dag import FabricStockDag
from factory.follow_stock_dag import FollowStockDag

def split_task(task, classname):
    if not classname:
        raise Exception("classname is invalid")
    factory = eval("{}(task)".format(classname))
    factory.create_subtasks()
    return factory.subtasks
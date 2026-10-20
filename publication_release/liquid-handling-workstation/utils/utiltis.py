import pandas as pd
import time
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
task_dir = os.path.dirname(current_dir) + "/tasks"


def split_task(file_name):
    task_file = os.path.join(task_dir, file_name)
    task_df = pd.read_excel(task_file)
    liquid_tasks = task_df[task_df["Station"] == "Liquid"]
    solid_tasks = task_df[task_df["Station"] == "Solid"]
    reactor_tasks = task_df[task_df["Station"] == "Reactor"]
    return liquid_tasks, solid_tasks, reactor_tasks
    pass


def generate_task_flows():
    pass

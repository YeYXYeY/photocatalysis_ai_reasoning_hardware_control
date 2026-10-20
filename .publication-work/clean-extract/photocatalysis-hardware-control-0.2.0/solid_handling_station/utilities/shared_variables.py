import threading

# coarse weighing flag
to_coarse_flag = True
# fine weighing flag
to_fine_flag = False
# micro weighing flag
to_micro_flag = False
# stop weighing flag
to_stop_flag = False
# coarse weighing event
coarse_event = threading.Event()
# fine weighing event
fine_event = threading.Event()
# micro weighing event
micro_event = threading.Event()
# weighing control event
control_event = threading.Event()
lock = threading.Lock()


if __name__ == "__main__":
    print(type(lock))

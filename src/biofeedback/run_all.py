import multiprocessing
from biofeedback.controller import run as controller_run
from biofeedback.acc_pipe import run as acc_pipe_run

def run():
    ctrl_proc = multiprocessing.Process(target=controller_run)
    acc_proc = multiprocessing.Process(target=acc_pipe_run)
    
    ctrl_proc.start()
    acc_proc.start()
    
    ctrl_proc.join()
    acc_proc.join
    
run()
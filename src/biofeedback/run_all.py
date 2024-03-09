import multiprocessing
from biofeedback.controller import run as controller_run
from biofeedback.acc_pipe import run as acc_pipe_run
# from biofeedback.hr_pipe import run as hr_pipe_run

def run():
    ctrl_proc = multiprocessing.Process(target=controller_run)
    acc_proc = multiprocessing.Process(target=acc_pipe_run)
    # hr_proc = multiprocessing.Process(target=hr_pipe_run)
    
    ctrl_proc.start()
    acc_proc.start()
    # hr_proc.start()
    
    ctrl_proc.join()
    acc_proc.join
    # hr_proc.join()
    
run()
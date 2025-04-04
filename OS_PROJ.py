from Scheduler.SchedulerSimulator import SchedulerSimulator
from Processses.Process import Process
import time
import threading
from collections import deque


if __name__ == "__main__":
    print("Select Scheduler in real time:")
    print("1. Yes\n2. No")
    
    choice_live = input("Enter choice (1-2): ")
    if choice_live == '1':
        live=1
    elif choice_live == '2':
        live=0

    print("Select Scheduler Type:")
    print("1. FCFS\n2. SJF\n3. Priority\n4. Round Robin")
    choice = input("Enter choice (1-4): ")

    if choice == '1':
        scheduler = SchedulerSimulator("FCFS")
    elif choice == '2':
        preemptive = input("Preemptive? (y/n): ").lower() == 'y'
        scheduler = SchedulerSimulator("SJF", preemptive=preemptive, live=live)
    elif choice == '3':
        preemptive = input("Preemptive? (y/n): ").lower() == 'y'
        scheduler = SchedulerSimulator("Priority", preemptive=preemptive)
    elif choice == '4':
        tq = int(input("Enter Time Quantum: "))
        scheduler = SchedulerSimulator("RR", time_quantum=tq)
    else:
        print("Invalid choice.")
        exit()

    n = int(input("Enter number of initial processes: "))
    for i in range(n):
        pid = i + 1
        at = int(input(f"Arrival time for P{pid}: "))
        bt = int(input(f"Burst time for P{pid}: "))
        pr = None
        if scheduler.scheduler_type == "Priority":
            pr = int(input(f"Priority for P{pid} (smaller is higher): "))
        scheduler.add_process(Process(pid, at, bt, pr))

    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=scheduler.run)
    scheduler_thread.start()
   


    # Allow dynamic process addition
    while scheduler_thread.is_alive():
        cmd = input("Add new process? (y/n): ").strip().lower()
        if cmd == 'y':
            pid = len(scheduler.processes) + 1
            at = int(input(f"Arrival time for P{pid}: "))
            bt = int(input(f"Burst time for P{pid}: "))
            pr = None
            if scheduler.scheduler_type == "Priority":
                pr = int(input(f"Priority for P{pid} (smaller is higher): "))
            scheduler.add_process(Process(pid, at, bt, pr))
        else:
            break
    

   
    scheduler_thread.join()
    

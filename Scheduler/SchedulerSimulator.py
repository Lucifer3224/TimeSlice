import time
import threading
from collections import deque
from Scheduler.SJF import SJF
from Scheduler.FCFS import FCFS
from Scheduler.Priority import Priority
from Scheduler.RR import RR
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class SchedulerSimulator(object):
       def __init__(self, scheduler_type, preemptive=False,live=1, time_quantum=None):
            self.scheduler_type = scheduler_type
            self.time_quantum = time_quantum
            self.preemptive = preemptive
            self.processes = []
            self.timeline = []
            self.time = 0
            self.running = False
            self.lock = threading.Lock()
            self.live=live



       def add_process(self, process):
            with self.lock:
                self.processes.append(process)




       def get_ready_processes(self):   #return array contain processes in not finished
            ReadyProcesses=[]
            for p in self.processes:
                if p.arrival_time <= self.time and p.remaining_time > 0:
                     ReadyProcesses.append(p)
            return ReadyProcesses



        
       def print_status(self):    
            with self.lock:
                print(f"\n🕒Time {self.time}s: ")
                for p in sorted(self.processes, key=lambda x: x.pid):   # print processes in an order (ID)
                    print(f"P{ p.pid } - Remaining Time: {  p.remaining_time }")
                print("----------------------------------------")


       
   

       def print_results(self):
            process_in_timeline = [f"P{pid}" for pid in self.timeline]
            gantt_line = " -> ".join(process_in_timeline)
            print("\n📊Gantt Chart:", gantt_line)
            waiting_times = []
            turnaround_times = []
            for p in self.processes:
                turnaround_t = p.completion_time - p.arrival_time
                waiting_t = turnaround_t - p.burst_time
                turnaround_times.append(turnaround_t)
                waiting_times.append(waiting_t)
            print(f"Average Waiting Time: {sum(waiting_times) / len(waiting_times):.2f}")
            print(f"Average Turnaround Time: {sum(turnaround_times) / len(turnaround_times):.2f}")
            print("Finish,cannot add new proccess")
          

       


       def run(self):
            self.running = True

            scheduler = None
            if self.scheduler_type == "FCFS":
                scheduler = FCFS(self)
            elif self.scheduler_type == "SJF":
                scheduler = SJF(self, self.preemptive,self.live)
            elif self.scheduler_type == "Priority":
                scheduler = Priority(self, self.preemptive)
            elif self.scheduler_type == "RR":
                scheduler = RR(self, self.time_quantum)
            if scheduler:
                scheduler.run()
                self.print_results()
            else:
                print("Invalid scheduler type.")
            
            



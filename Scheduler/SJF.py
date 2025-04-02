import time

class SJF:
    def __init__(self, simulator, preemptive=False):
        self.sim = simulator    # instance of ScheduleSimulator
        self.preemptive = preemptive

    def run(self):
        completed = set()  # automatically removes duplicates & order it 

        while self.sim.running and len(completed) < len(self.sim.processes):  
            ready=[]    # ready array contain all processes not finished
            for p in self.sim.get_ready_processes():
                if p.pid not in completed:  #true all time (check)
                    ready.append(p)

            if ready:
                ready.sort(key=lambda p: (p.remaining_time, p.arrival_time))  #small fn sort array ready by remaining_time if same sort by arrival_time 
                p = ready[0]

                if p.start_time is None:
                    p.start_time = self.sim.time

                if self.preemptive:
                    time.sleep(1)    # to make real-time simulation
                    p.remaining_time -= 1
                    self.sim.timeline.append(p.pid)
                    self.sim.print_status()
                    self.sim.time += 1
                    if p.remaining_time == 0:
                        p.completion_time = self.sim.time
                        completed.add(p.pid)
                #else:
                    #non preemptive fun 
                
                    


            else:   #no process in ready array 
                time.sleep(1)
                self.sim.timeline.append("Idle")
                self.sim.print_status()
                self.sim.time += 1

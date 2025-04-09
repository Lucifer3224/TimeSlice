class PriorityScheduler:
    def __init__(self, processes):
      self.waiting_queue=list(processes)
      self.ready_queue=[]
      self.waiting_queue.sort(key=lambda x:x[2])

      """
      Initialize the Priority Scheduler

      Args:
          processes: List of process tuples (name, burst_time, arrival_time, priority, is_preemptive)
          Lower priority number means higher priority
      """
    def update_queues(self, current_time):
      """
      Move arrived processes from waiting to ready queue.
      """    
      newly_arrived=[]
      still_waiting=[]
      for p in self.waiting_queue:
        if p[2]<=current_time:
          newly_arrived.append(p)
        else:
          still_waiting.append(p)
          self.waiting_queue=still_waiting
      for p in newly_arrived:
        self.ready_queue.append(p)
        return newly_arrived
        

    def run_non_preemptive(self, current_time):
      if not self.ready_queue:
        return None, 0
        self.ready_queue.sort(key=lambda x:x[3])
        selected_process=self.ready_queue.pop(0)
        remaining_time=selected_process[1]
        return selected_process,remaining_time
        
        """
        Args:
            current_time: Current simulation time

        Returns:
            tuple: (selected_process, remaining_time) or (None, 0) if no process is selected
        """

    def run_preemptive(self, current_time, current_process=None, remaining_time=0):
        """
        Args:
            current_time: Current simulation time
            current_process: Process currently running (if any)
            remaining_time: Remaining time of current process

        Returns:
            tuple: (selected_process, remaining_time, preempted)
        """
        if not current_process:
            process, time = self.run_non_preemptive(current_time)
            return process, time, False
        for new_job in self.ready_queue:
            if new_job[3] < current_process[3]:
                updated_process = list(current_process)
                updated_process[1] = remaining_time
                self.ready_queue.append(tuple(updated_process))
                self.ready_queue.sort(key=lambda x: x[3])
                selected_process = self.ready_queue.pop(0)
                new_remaining_time = selected_process[1]
                return selected_process, new_remaining_time, True
      

    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0

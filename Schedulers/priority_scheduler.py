class Process:
    def __init__(self, name, burst_time, arrival_time, priority=0, is_preemptive=False):
      self.name = name
      self.burst_time = burst_time
      self.arrival_time = arrival_time
      self.priority = priority
      self.is_preemptive = is_preemptive
      self.remaining_time = burst_time
      self.start_time = None
      self.completion_time = None

class PriorityScheduler:
    def __init__(self, processes):
      self.waiting_queue=list(processes)
      self.ready_queue=[]
      self.time = 0
      self.original_processes = [Process(name, bt, at, priority, is_preemptive) for (name, bt, at, priority, is_preemptive) in processes]
      self.waiting_queue = self.original_processes.copy()
      self.ready_queue = []
      self.timeline = []
      self.completed = []

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
        if p.arrival_time <= current_time:
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
      self.ready_queue.sort(key=lambda p: (p.priority, p.arrival_time))
      selected_process=self.ready_queue.pop(0)
      remaining_time=selected_process.burst_time
      if selected_process.start_time is None:
        selected_process.start_time=current_time
      if remaining_time == 0:
        current_process.completion_time = current_time
        scheduler.completed.append(current_process)
        current_process = None
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

        if not current_process.is_preemptive:
          return current_process, remaining_time, False  # No time deduction here

        # Find highest priority in ready queue
        if self.ready_queue:
          highest_prio = min(p.priority for p in self.ready_queue)
          if highest_prio < current_process.priority:
              # Preemption logic
              current_process.remaining_time = remaining_time
              self.ready_queue.append(current_process)
              self.ready_queue.sort(key=lambda p: (p.priority, p.arrival_time))
              new_process = self.ready_queue.pop(0)
              return new_process, new_process.remaining_time, True

        # No preemption
        return current_process, remaining_time, False



    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0

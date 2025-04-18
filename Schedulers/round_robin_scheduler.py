class RoundRobinScheduler:
    def __init__(self, processes, default_quantum=2):
        """
        Initialize the Round Robin Scheduler
        
        Args:
            processes: List of process tuples (name, burst_time, arrival_time, time_quantum)
            default_quantum: Default time quantum if not specified in process
        """
        self.waiting_queue = list(processes)
        self.ready_queue = []
        self.default_quantum = default_quantum
        # Sort initially by arrival time
        self.waiting_queue.sort(key=lambda x: x[2])
        
    def update_queues(self, current_time):
        """Move arrived processes from waiting to ready queue."""
        newly_arrived = []
        still_waiting = []
        
        for proc in self.waiting_queue:
            if proc[2] <= current_time:  # Check arrival time
                newly_arrived.append(proc)
            else:
                still_waiting.append(proc)
                
        self.waiting_queue = still_waiting
        for proc in newly_arrived:
            self.ready_queue.append(proc)
            
        return newly_arrived
    
    def run(self, current_time, current_process=None, remaining_time=0, time_quantum_left=0):
        """
        Round Robin: Select next process or continue current process within time quantum.
        
        Args:
            current_time: Current simulation time
            current_process: Process currently running (if any)
            remaining_time: Remaining time of current process
            time_quantum_left: Remaining time quantum
            
        Returns:
            Tuple of (selected_process, remaining_time, time_quantum_left, preempted_flag)
        """
        # If time quantum expired and there are more processes, perform context switch
        if current_process and time_quantum_left == 0 and remaining_time > 0:
            # Current process needs to go back to ready queue
            updated_process = list(current_process)
            updated_process[1] = remaining_time
            self.ready_queue.append(tuple(updated_process))
            
            # Process completed its time quantum, need a new process
            process, burst, quantum = self._get_next_process()
            return process, burst, quantum, True
        
        # If there's no current process or it's completed, get a new one
        if not current_process or remaining_time <= 0:
            process, burst, quantum = self._get_next_process()
            return process, burst, quantum, False
            
        # Continue with current process
        return current_process, remaining_time, time_quantum_left, False
    
    def _get_next_process(self):
        """Get the next process from ready queue with its time quantum."""
        if not self.ready_queue:
            return None, 0, 0
            
        selected_process = self.ready_queue.pop(0)
        remaining_time = selected_process[1]  # Burst time
        
        # Determine time quantum
        if len(selected_process) > 3:
            time_quantum = selected_process[3]
        else:
            time_quantum = self.default_quantum
            
        return selected_process, remaining_time, time_quantum
        
    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0
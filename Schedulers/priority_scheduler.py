class PriorityScheduler:
    def __init__(self, processes):
        """
        Initialize the Priority Scheduler
        
        Args:
            processes: List of process tuples (name, burst_time, arrival_time, priority, is_preemptive)
            Lower priority number means higher priority
        """
        self.waiting_queue = list(processes)
        self.ready_queue = []
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
    
    def run_non_preemptive(self, current_time):
        """
        Non-preemptive Priority: Select process with highest priority.
        
        Returns:
            Tuple of (selected_process, remaining_time) or (None, 0) if no process is selected
        """
        if not self.ready_queue:
            return None, 0
            
        # Sort ready queue by:
        # 1. priority (lower number = higher priority)
        # 2. burst time (shorter = higher priority) as tiebreaker
        # 3. arrival time (earlier = higher priority) as second tiebreaker
        self.ready_queue.sort(key=lambda x: (x[3], x[1], x[2]))
        selected_process = self.ready_queue.pop(0)
        remaining_time = selected_process[1]  # Burst time
        
        return selected_process, remaining_time
    
    def run_preemptive(self, current_time, current_process=None, remaining_time=0):
        """
        Preemptive Priority: Check if higher priority job has arrived.
        Also prioritizes shorter burst times when priority and arrival time are equal.
        
        Args:
            current_time: Current simulation time
            current_process: Process currently running (if any)
            remaining_time: Remaining time of current process
            
        Returns:
            Tuple of (selected_process, remaining_time, preempted)
        """
        # If there's no current process, behave like non-preemptive
        if not current_process:
            process, time = self.run_non_preemptive(current_time)
            return process, time, False
        
        # Build a list of candidate processes (current + ready queue)
        candidates = []
        
        # Add current process
        candidates.append({
            'process': current_process,
            'priority': current_process[3],  # Priority
            'remaining': remaining_time,     # Remaining time
            'arrival': current_process[2]    # Arrival time
        })
        
        # Add processes from ready queue
        for proc in self.ready_queue:
            candidates.append({
                'process': proc,
                'priority': proc[3],   # Priority
                'remaining': proc[1],  # Burst time
                'arrival': proc[2]     # Arrival time
            })
        
        # Sort by priority, then by remaining time, then by arrival
        candidates.sort(key=lambda x: (x['priority'], x['remaining'], x['arrival']))
        best_candidate = candidates[0]
        
        # If best candidate is not current process, preemption occurs
        if best_candidate['process'] != current_process:
            # Add current process back to ready queue with updated remaining time
            updated_process = list(current_process)
            updated_process[1] = remaining_time
            self.ready_queue.append(tuple(updated_process))
            
            # Remove selected process from ready queue
            selected_process = best_candidate['process']
            try:
                self.ready_queue.remove(selected_process)
            except ValueError:
                # Process might have been modified, search by name
                process_name = selected_process[0]
                for i, proc in enumerate(self.ready_queue):
                    if proc[0] == process_name:
                        self.ready_queue.pop(i)
                        break
            
            return selected_process, best_candidate['remaining'], True
        
        # No preemption needed
        return current_process, remaining_time, False
        
    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0
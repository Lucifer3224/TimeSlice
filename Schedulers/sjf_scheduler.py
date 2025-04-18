class SJFScheduler:
    def __init__(self, processes):
        """
        Initialize the SJF Scheduler
        
        Args:
            processes: List of process tuples (name, burst_time, arrival_time, is_preemptive)
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
                self.ready_queue.append(proc)
            else:
                still_waiting.append(proc)
                
        self.waiting_queue = still_waiting
        return newly_arrived
    
    def run_non_preemptive(self, current_time):
        """
        Non-preemptive SJF: Decide which process to run based on arrival and burst time.
        
        Returns:
            Tuple of (selected_process, remaining_time) or (None, 0) if no process is selected
        """
        if not self.ready_queue:
            return None, 0
            
        # Sort ready queue by burst time for SJF
        self.ready_queue.sort(key=lambda x: x[1])
        selected_process = self.ready_queue.pop(0)
        remaining_time = selected_process[1]  # Burst time
        
        return selected_process, remaining_time
    
    def run_preemptive(self, current_time, current_process=None, remaining_time=0):
        """
        Preemptive SJF (SRTF): Pick job with shortest remaining time each tick.
        Decisions are made based on the state at current_time.

        Args:
            current_time: Current simulation time.
            current_process: Currently running process tuple (if any).
            remaining_time: Remaining burst time of current_process.

        Returns:
            Tuple of (selected_process, remaining_time_of_selected, was_preempted).
            Returns (None, 0, False) if no process is ready or running.
        """
        # Ensure the ready queue is up-to-date with newly arrived processes
        self.update_queues(current_time)

        potential_candidates = []

        # Add the currently running process (if any) to candidates
        if current_process and remaining_time > 0:
            potential_candidates.append({
                'process': current_process, 
                'time_left': remaining_time,
                'arrival': current_process[2]
            })

        # Add processes from the ready queue to candidates
        for proc in self.ready_queue:
            # Safety check: ensure the process tuple has enough elements
            if len(proc) >= 3:
                potential_candidates.append({
                    'process': proc,
                    'time_left': proc[1],  # Burst time
                    'arrival': proc[2]    # Arrival time
                })

        # If no candidates (neither running nor ready), CPU is idle
        if not potential_candidates:
            return None, 0, False

        # Sort candidates: 1st by shortest time_left, 2nd by earliest arrival time
        potential_candidates.sort(key=lambda x: (x['time_left'], x['arrival']))

        # Select the best candidate
        shortest_candidate = potential_candidates[0]
        selected_process = shortest_candidate['process']
        selected_process_time_left = shortest_candidate['time_left']

        was_preempted = False

        # Determine if preemption occurred
        if current_process:
            if selected_process != current_process:
                # Preemption occurred
                was_preempted = True
                
                # Add the preempted process back to the ready queue
                # Update its tuple with its remaining time before adding
                if remaining_time > 0:  # Only add back if there's time left
                    preempted_process_updated = list(current_process)
                    preempted_process_updated[1] = remaining_time # Store remaining time
                    self.ready_queue.append(tuple(preempted_process_updated))

                # Remove the selected process from ready queue 
                try:
                    if selected_process in self.ready_queue:
                        self.ready_queue.remove(selected_process)
                except ValueError:
                    # Process might have been modified, search by name
                    process_name = selected_process[0]
                    for i, proc in enumerate(self.ready_queue):
                        if proc[0] == process_name:
                            self.ready_queue.pop(i)
                            break

        else: # No current process was running, starting a new one
            if selected_process:
                # Remove the selected process from ready queue as it's now running
                try:
                    if selected_process in self.ready_queue:
                        self.ready_queue.remove(selected_process)
                except ValueError:
                    # Process might have been modified, search by name
                    process_name = selected_process[0]
                    for i, proc in enumerate(self.ready_queue):
                        if proc[0] == process_name:
                            self.ready_queue.pop(i)
                            break
        
        # Return the selected process, its remaining time, and preemption status
        return selected_process, selected_process_time_left, was_preempted
        
    def remove_completed_process(self, process_tuple):
        """Remove a completed process from internal queues."""
        # Attempt to remove from ready queue (might be there if preempted just before finishing)
        try:
            # Need to find by name as the tuple might have different remaining time
            proc_to_remove = next(p for p in self.ready_queue if p[0] == process_tuple[0])
            self.ready_queue.remove(proc_to_remove)
        except (StopIteration, ValueError):
            pass # Not found in ready queue, which is normal if it ran to completion

        # Also check waiting queue just in case (shouldn't normally happen)
        try:
            proc_to_remove = next(p for p in self.waiting_queue if p[0] == process_tuple[0])
            self.waiting_queue.remove(proc_to_remove)
        except (StopIteration, ValueError):
            pass

    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0
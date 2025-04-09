class FCFSScheduler:
    def __init__(self, processes):
        """
        Initialize the FCFS Scheduler

        Args:
            processes: List of process tuples (name, burst_time, arrival_time)
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

    def run(self, current_time):
        """
        FCFS: Select the first process that arrived.

        Returns:
            Tuple of (selected_process, remaining_time) or (None, 0) if no process is selected
        """
        if not self.ready_queue:
            return None, 0

        # FCFS just takes the first process in the ready queue
        selected_process = self.ready_queue.pop(0)
        remaining_time = selected_process[1]  # Burst time

        return selected_process, remaining_time

    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0
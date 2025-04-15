class RoundRobinScheduler:
    def __init__(self, processes, default_quantum=2):
        """
        Initialize the Round Robin Scheduler

        Args:
            processes: List of process tuples (name, burst_time, arrival_time, time_quantum)
            default_quantum: Default time quantum if not specified in process
        """
        self.original_processes = [
            (name, burst, arrival, quantum)
            for name, burst, arrival, quantum in processes
        ]
        self.waiting_queue = self.original_processes.copy()
        self.ready_queue = []
        self.timeline = []
        self.completed = []
        self.default_quantum = default_quantum

    def update_queues(self, current_time):
        """
        Move arrived processes from waiting to ready queue.

        Args:
            current_time: Current simulation time

        Returns:
            list: Newly arrived processes
        """
        newly_arrived = []
        for proc in list(self.waiting_queue):
            name, burst, arrival, quantum = proc
            if arrival <= current_time:
                self.ready_queue.append(proc)
                self.waiting_queue.remove(proc)
                newly_arrived.append(proc)
        return newly_arrived

    def run(self, current_time, current_process=None, remaining_time=0, time_quantum=0):
        """
        Round Robin: Select next process or continue current process within time quantum.

        Args:
            current_time: Current simulation time
            current_process: Process currently running (if any)
            remaining_time: Remaining time of current process
            time_quantum: Remaining time quantum

        Returns:
            list: [(selected_process_name, exec_time, time_quantum)]
        """
        self.update_queues(current_time)

        if not self.ready_queue:
            return None

        name, burst, arrival, quantum = self._get_next_process()

        exec_time = min(burst, quantum)
        self.timeline.extend([name] * exec_time)

        new_burst = burst - exec_time

        if new_burst > 0:
            # Requeue with updated burst and new arrival (simulate delay)
            self.ready_queue.append((name, new_burst, current_time + exec_time, quantum))
        else:
            self.completed.append((name, burst, arrival, quantum))

        return [(name, exec_time, quantum)]

    def _get_next_process(self):
        """
        Get the next process from ready queue.

        Returns:
            tuple: (name, burst, arrival, quantum)
        """
        if self.ready_queue:
            return self.ready_queue.pop(0)
        return None

    def is_done(self):
        """Check if scheduler has completed all processes."""
        return not self.ready_queue and not self.waiting_queue

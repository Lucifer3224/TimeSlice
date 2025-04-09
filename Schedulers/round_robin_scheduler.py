class RoundRobinScheduler:
    def __init__(self, processes, default_quantum=2):
        """
        Initialize the Round Robin Scheduler

        Args:
            processes: List of process tuples (name, burst_time, arrival_time, time_quantum)
            default_quantum: Default time quantum if not specified in process
        """
        pass

    def update_queues(self, current_time):
        """
        Move arrived processes from waiting to ready queue.

        Args:
            current_time: Current simulation time

        Returns:
            list: Newly arrived processes
        """
        pass

    def run(self, current_time, current_process=None, remaining_time=0, time_quantum=0):
        """
        Round Robin: Select next process or continue current process within time quantum.

        Args:
            current_time: Current simulation time
            current_process: Process currently running (if any)
            remaining_time: Remaining time of current process
            time_quantum: Remaining time quantum

        Returns:
            tuple: (selected_process, remaining_time, time_quantum, is_new_process)
        """
        pass

    def _get_next_process(self):
        """
        Get the next process from ready queue with its time quantum.

        Returns:
            tuple: (selected_process, remaining_time, time_quantum)
        """
        pass

    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0
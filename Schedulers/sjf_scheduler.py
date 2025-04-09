class SJFScheduler:
    def __init__(self, processes):
        """
        Initialize the SJF Scheduler

        Args:
            processes: List of process tuples (name, burst_time, arrival_time, is_preemptive)
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

    def run_non_preemptive(self, current_time):
        """
        Non-preemptive SJF: Decide which process to run based on arrival and burst time.

        Args:
            current_time: Current simulation time

        Returns:
            tuple: (selected_process, remaining_time) or (None, 0) if no process is selected
        """
        pass

    def run_preemptive(self, current_time, current_process=None, remaining_time=0):
        """
        Preemptive SJF (SRTF): Pick job with shortest remaining time each tick.

        Args:
            current_time: Current simulation time
            current_process: Process currently running (if any)
            remaining_time: Remaining time of current process

        Returns:
            tuple: (selected_process, remaining_time, preempted)
        """
        pass

    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0
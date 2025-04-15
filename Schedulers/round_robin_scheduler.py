from collections import deque
from sjf_scheduler import process  # Assuming the 'process' class exists with burst_time, arrival_time, remaining_time


class RoundRobinScheduler:
    def __init__(self, processes, default_quantum=2):
        """
        Initialize the Round Robin Scheduler

        Args:
            processes: List of process tuples (name, burst_time, arrival_time, time_quantum)
            default_quantum: Default time quantum if not specified in process
        """
        self.default_quantum = default_quantum
        self.time = 0
        self.original_processes = []
        self.waiting_queue = []
        self.ready_queue = deque()
        self.timeline = []
        self.completed = []

        for entry in processes:
            if len(entry) == 3:
                name, bt, at = entry
                tq = default_quantum
            else:
                name, bt, at, tq = entry
            p = process(name, bt, at)
            p.time_quantum = tq
            self.original_processes.append(p)
            self.waiting_queue.append(p)
    

    def update_queues(self, current_time):
        """
        Move arrived processes from waiting to ready queue.

        Args:
            current_time: Current simulation time

        Returns:
            list: Newly arrived processes
        """
        newly_arrived = []
        for p in list(self.waiting_queue):
            if p.arrival_time <= current_time:
                self.ready_queue.append((p, p.time_quantum))  # (process, remaining_quantum)
                self.waiting_queue.remove(p)
                newly_arrived.append(p)
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
            tuple: (selected_process, remaining_time, time_quantum, is_new_process)
        """
        self.update_queues(current_time)

        # If we are continuing a process
        if current_process and remaining_time > 0 and time_quantum > 0:
            self.timeline.append(current_process.name)
            remaining_time -= 1
            time_quantum -= 1
            self.time += 1
            self.update_queues(self.time)
            if remaining_time == 0:
                current_process.completion_time = self.time
                self.completed.append(current_process)
                return None, 0, 0, False
            if time_quantum == 0:
                self.ready_queue.append((current_process, current_process.time_quantum))
                return None, 0, 0, False
            return current_process, remaining_time, time_quantum, False

        # If CPU is idle
        if not self.ready_queue:
            self.timeline.append("Idle")
            self.time += 1
            return None, 0, 0, False

        # Get next process from ready queue
        next_process, quantum = self._get_next_process()
        if next_process.start_time is None:
            next_process.start_time = self.time

        self.timeline.append(next_process.name)
        next_process.remaining_time -= 1
        quantum -= 1
        self.time += 1
        self.update_queues(self.time)

        if next_process.remaining_time == 0:
            next_process.completion_time = self.time
            self.completed.append(next_process)
            return None, 0, 0, True
        if quantum == 0:
            self.ready_queue.append((next_process, next_process.time_quantum))
            return None, 0, 0, True
        return next_process, next_process.remaining_time, quantum, True

    def _get_next_process(self):
        """
        Get the next process from ready queue with its time quantum.

        Returns:
            tuple: (selected_process, remaining_time, time_quantum)
        """
        return self.ready_queue.popleft()

    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0
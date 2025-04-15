from collections import deque

class process:
    def __init__(self, name, burst_time, arrival_time):
        """
        Represents a process in CPU scheduling.

        Args:
            name (str): Name of the process (e.g., "P1")
            burst_time (int): Total CPU burst time required
            arrival_time (int): Time at which the process arrives in the system
        """
        self.name = name
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.remaining_time = burst_time  # Remaining time during execution
        self.start_time = None  # Time when the process starts execution
        self.completion_time = None  # Time when the process finishes execution
        self.time_quantum = None  # Optional: Time quantum (used in Round Robin)

    def turnaround_time(self):
        """
        Calculates turnaround time.

        Returns:
            int: Turnaround Time = Completion Time - Arrival Time
        """
        return self.completion_time - self.arrival_time if self.completion_time is not None else None

    def waiting_time(self):
        """
        Calculates waiting time.

        Returns:
            int: Waiting Time = Turnaround Time - Burst Time
        """
        tat = self.turnaround_time()
        return tat - self.burst_time if tat is not None else None

    def __repr__(self):
        return f"{self.name}(AT={self.arrival_time}, BT={self.burst_time}, RT={self.remaining_time})"



class RoundRobinScheduler:
    def __init__(self, processes, default_quantum=2):
        """
        Initialize the Round Robin Scheduler

        Args:
            processes: List of process objects (name, burst_time, arrival_time)
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
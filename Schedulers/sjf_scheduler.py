class Process:
    def _init_(self, name, burst_time, arrival_time):
        self.name = name
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.remaining_time = burst_time
        self.start_time = None
        self.completion_time = None


class SJFScheduler:
    def _init_(self, processes):
        """
        Initialize the SJF Scheduler

        Args:
            processes: List of process tuples (name, burst_time, arrival_time, is_preemptive)
        """
        self.time = 0
        self.original_processes = [
            Process(name, bt, at) for name, bt, at, _ in processes
        ]
        self.waiting_queue = self.original_processes.copy()
        self.ready_queue = []
        self.timeline = []
        self.completed = []

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
                self.ready_queue.append(p)
                newly_arrived.append(p)
                self.waiting_queue.remove(p)
        return newly_arrived





    def run_non_preemptive(self, current_time):
        """
        Non-preemptive SJF: Decide which process to run based on arrival and burst time.

        Args:
            current_time: Current simulation time

        Returns:
            tuple: (selected_process, remaining_time) or (None, 0) if no process is selected
        """
        





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
        self.update_queues(current_time)
        self.ready_queue = [p for p in self.ready_queue if p.remaining_time > 0]

        if not self.ready_queue:
            return None, 0, False

        self.ready_queue.sort(key=lambda p: (p.remaining_time, p.arrival_time))
        selected = self.ready_queue[0]

        if selected.start_time is None:
            selected.start_time = current_time

        selected.remaining_time -= 1
        self.timeline.append(selected.name)
        self.time = current_time + 1

        if selected.remaining_time == 0:
            selected.completion_time = self.time
            self.ready_queue.remove(selected)
            self.completed.append(selected)

        preempted = current_process is not None and current_process != selected
        return selected, selected.remaining_time, preempted

    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0

# Assuming SJFScheduler and Process class are defined above

def print_summary(scheduler, mode):
    print(f"\n=== Gantt Chart ({mode}) ===")
    print(" -> ".join(scheduler.timeline))

    total_waiting = 0
    total_turnaround = 0
    print(f"\n{'Process':<8} {'Arrival':<8} {'Burst':<6} {'Start':<6} {'Completion':<10} {'Waiting':<8} {'Turnaround':<10}")
    for p in sorted(scheduler.completed, key=lambda x: x.name):
        turnaround = p.completion_time - p.arrival_time
        waiting = turnaround - p.burst_time
        total_waiting += waiting
        total_turnaround += turnaround
        print(f"{p.name:<8} {p.arrival_time:<8} {p.burst_time:<6} {p.start_time:<6} {p.completion_time:<10} {waiting:<8} {turnaround:<10}")

    n = len(scheduler.completed)
    print(f"\nAverage Waiting Time: {total_waiting / n:.2f}")
    print(f"Average Turnaround Time: {total_turnaround / n:.2f}")


#     # Sample process list: (name, burst_time, arrival_time, is_preemptive)
# processes = [
#     ("P1", 7, 0, True),
#     ("P2", 4, 2, True),
#     ("P3", 1, 4, True),
#     ("P4", 4, 5, True)
# ]


# # ========== Preemptive Simulation ==========
# preemptive_scheduler = SJFScheduler(processes)
# print("\n===== Running Preemptive SJF (SRTF) =====")
# current_process = None
# remaining_time = 0
# while not preemptive_scheduler.is_done():
#     current_process, remaining_time, _ = preemptive_scheduler.run_preemptive(
#         preemptive_scheduler.time,
#         current_process=current_process,
#         remaining_time=remaining_time
#     )

# print_summary(preemptive_scheduler, "Preemptive SJF (SRTF)")
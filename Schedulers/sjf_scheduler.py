class SJFScheduler:
    def __init__(self, tasks):
        self.tasks = tasks
        self.pending_tasks = [(task_name, arrival_time, burst_time) for task_name, arrival_time, burst_time in tasks]
        self.ready_queue = []
        self.completed_tasks = []
        self.timeline = []

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
        for task in list(self.pending_tasks):
            if task[1] <= current_time:
                self.ready_queue.append(task)
                self.pending_tasks.remove(task)
        if not self.ready_queue:
            return None, 0
        self.ready_queue.sort(key=lambda x: x[2])
        selected_task = self.ready_queue.pop(0)
        remaining_time = selected_task[2]
        self.timeline.extend([selected_task[0]] * remaining_time)
        self.completed_tasks.append(selected_task)

        return selected_task, remaining_time

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

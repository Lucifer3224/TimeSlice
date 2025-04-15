class process:
    def __init__(self, name, burst_time, arrival_time):
        self.name = name
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.remaining_time = burst_time
        self.start_time = None
        self.completion_time = None

class PriorityProcess(process):
    def __init__(self, name, burst_time, arrival_time, priority):
        super().__init__(name, burst_time, arrival_time)
        self.priority = priority

class PriorityScheduler:
    def __init__(self, processes):
        self.time = 0
        self.original_processes = []
        for p in processes:
            if len(p) == 5:
                name, bt, at, pr, _ = p  # ignore preemptive flag for now
            else:
                name, bt, at, pr = p
            self.original_processes.append(PriorityProcess(name, bt, at, pr))

        self.waiting_queue = self.original_processes.copy()
        self.ready_queue = []
        self.timeline = []
        self.completed = []

    def update_queues(self, current_time):
        newly_arrived = []
        for p in list(self.waiting_queue):
            if p.arrival_time <= current_time:
                self.ready_queue.append(p)
                newly_arrived.append(p)
                self.waiting_queue.remove(p)
        return newly_arrived

    def run_preemptive(self, current_time, current_process=None, remaining_time=0):
        self.update_queues(current_time)
        self.ready_queue = [p for p in self.ready_queue if p.remaining_time > 0] # ready_queue array contain all processes not finished

        if not self.ready_queue:
            self.timeline.append("Idle")
            self.time += 1
            return None, 0, False #different return

        # Sort by priority (lower value means higher priority), then arrival time
        self.ready_queue.sort(key=lambda p: (p.priority, p.arrival_time))
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

    def run_non_preemptive(self, current_time):
        self.update_queues(current_time)
        self.ready_queue = [p for p in self.ready_queue if p.remaining_time > 0]

        if not self.ready_queue:
            self.timeline.append("Idle")
            self.time += 1
            return None, 1

        # Sort by priority (lower number = higher priority), then arrival time
        self.ready_queue.sort(key=lambda p: (p.priority, p.arrival_time))
        selected = self.ready_queue[0]

        if selected.start_time is None:
            selected.start_time = self.time

        for _ in range(selected.remaining_time):
            self.timeline.append(selected.name)
            self.time += 1

        selected.remaining_time = 0
        selected.completion_time = self.time
        self.ready_queue.remove(selected)
        self.completed.append(selected)

        return selected, selected.burst_time

    def is_done(self):
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0

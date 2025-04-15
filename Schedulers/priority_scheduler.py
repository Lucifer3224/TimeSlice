class PriorityScheduler:
    def __init__(self, tasks):
        self.tasks = tasks
        self.pending_tasks = [
            (task_name, arrival_time, burst_time, priority) for task_name, arrival_time, burst_time, priority in tasks
        ]
        self.ready_queue = []
        self.completed_tasks = []
        self.timeline = []

    def update_queues(self, current_time):
        for task in list(self.pending_tasks):
            task_name, arrival_time, burst_time, priority = task
            if arrival_time <= current_time:
                # Add task with extra field: original burst time for later use
                self.ready_queue.append([task_name, arrival_time, burst_time, priority, burst_time])
                self.pending_tasks.remove(task)

    def run_preemptive(self, current_time=0):
        current_task = None

        while self.pending_tasks or self.ready_queue or current_task:
            self.update_queues(current_time)

            if current_task:
                self.ready_queue.append(current_task)
                current_task = None

            if not self.ready_queue:
                self.timeline.append("Idle")
                current_time += 1
                continue

            # Sort ready queue by priority (lower number = higher priority)
            self.ready_queue.sort(key=lambda x: x[3])
            current_task = self.ready_queue.pop(0)

            self.timeline.append(current_task[0])
            current_task[2] -= 1  # Reduce remaining burst time

            if current_task[2] == 0:
                # Append task using original burst time (stored in index 4)
                self.completed_tasks.append((current_task[0], current_task[1], current_task[4], current_task[3]))
                current_task = None

            current_time += 1

    def run_non_preemptive(self, current_time):
        for task in list(self.pending_tasks):
            if task[1] <= current_time:
                self.ready_queue.append(task)
                self.pending_tasks.remove(task)

        if not self.ready_queue:
            return None, 0

        self.ready_queue.sort(key=lambda x: x[3])
        selected_task = self.ready_queue.pop(0)
        remaining_time = selected_task[2]
        self.timeline.extend([selected_task[0]] * remaining_time)
        self.completed_tasks.append(selected_task)
        return selected_task, remaining_time


def print_summary(scheduler, mode="priority"):
    print(f"\n=== Gantt Chart ({mode}) ===")
    print(" -> ".join(scheduler.timeline))

    task_times = {}  # {task_name: [start_time, completion_time]}
    for time, task in enumerate(scheduler.timeline):
        if task == "Idle":
            continue
        if task not in task_times:
            task_times[task] = [time, time]
        else:
            task_times[task][1] = time

    total_waiting = 0
    total_turnaround = 0

    print(f"\n{'Process':<10} {'Arrival':<8} {'Burst':<6} {'Priority':<8} {'Start':<6} {'Completion':<10} {'Waiting':<8} {'Turnaround':<10}")
    for name, arrival, burst, priority in sorted(scheduler.completed_tasks, key=lambda x: x[0]):
        start = task_times[name][0]
        completion = task_times[name][1] + 1  # +1 since last execution happens at that index
        turnaround = completion - arrival
        waiting = turnaround - burst
        total_waiting += waiting
        total_turnaround += turnaround

        print(f"{name:<10} {arrival:<8} {burst:<6} {priority:<8} {start:<6} {completion:<10} {waiting:<8} {turnaround:<10}")

    n = len(scheduler.completed_tasks)
    if n > 0:
        print(f"\nAverage Waiting Time   : {total_waiting / n:.2f}")
        print(f"Average Turnaround Time: {total_turnaround / n:.2f}")


# Example usage
#tasks = [
#    ("P1", 0, 7, 4),
#    ("P2", 2, 4, 2),
#    ("P3", 4, 1, 1),
#    ("P4", 5, 4, 3),
#]

#scheduler = PriorityScheduler(tasks)
#scheduler.run_preemptive(current_time=0)
#print_summary(scheduler, mode="Preemptive Priority")


class SJFScheduler:

    def __init__(self, tasks):
        self.tasks = tasks
        self.pending_tasks = []
        for task in tasks:
            if len(task) == 4:
                task_name, burst_time, arrival_time, _ = task
            else:
                task_name, burst_time, arrival_time = task
            self.pending_tasks.append((task_name, arrival_time, burst_time))

        self.ready_queue = []
        self.completed_tasks = []
        self.timeline = []
        #
        self.waiting_queue = self.pending_tasks.copy()

    def update_queues(self, current_time):
        newly_arrived = []
        for task in list(self.pending_tasks):
            task_name, arrival_time, burst_time = task
            if arrival_time <= current_time:
                self.ready_queue.append([task_name, arrival_time, burst_time, burst_time])  # Add remaining time
                self.pending_tasks.remove(task)
                newly_arrived.append(task)
        return newly_arrived

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

    def run_preemptive(self, current_time, current_process=None, remaining_time=0, time_quantum=0):
        self.update_queues(current_time)

        if current_process:
            self.ready_queue.append(current_process)

        if not self.ready_queue:
            self.timeline.append("Idle")
            return None, 0, False  # Return 3 values

        self.ready_queue.sort(key=lambda x: x[2])  # Sort by remaining time (burst time)
        selected_task = self.ready_queue.pop(0)
        selected_task = list(selected_task) + [selected_task[2]]  # add remaining time if not already

        self.timeline.append(selected_task[0])
        selected_task[3] -= 1  # remaining time - 1

        preempted = current_process is not None and current_process[0] != selected_task[0]

        if selected_task[3] == 0:
            self.completed_tasks.append((selected_task[0], selected_task[1], selected_task[2]))
            return None, 0, preempted
        else:
            return selected_task, selected_task[3], preempted

    def is_done(self):
        """Check if scheduler has completed all processes."""
        return len(self.waiting_queue) == 0 and len(self.ready_queue) == 0





def print_summary(scheduler, mode="SJF"):
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

    print(f"\n{'Process':<10} {'Arrival':<8} {'Burst':<6} {'Start':<6} {'Completion':<10} {'Waiting':<8} {'Turnaround':<10}")
    for name, arrival, burst in sorted(scheduler.completed_tasks, key=lambda x: x[0]):
        start = task_times[name][0]
        completion = task_times[name][1] + 1  # +1 since last execution happens at that index
        turnaround = completion - arrival
        waiting = turnaround - burst
        total_waiting += waiting
        total_turnaround += turnaround

        print(f"{name:<10} {arrival:<8} {burst:<6} {start:<6} {completion:<10} {waiting:<8} {turnaround:<10}")

    n = len(scheduler.completed_tasks)
    if n > 0:
        print(f"\nAverage Waiting Time   : {total_waiting / n:.2f}")
        print(f"Average Turnaround Time: {total_turnaround / n:.2f}")



# tasks = [
#     ("P1", 0, 7),
#     ("P2", 2, 4),
#     ("P3", 4, 1),
#     ("P4", 5, 4),
# ]
# t = [
#      ("P1", 8, 1),
#      ("P2", 4, 1),
#      ("P3", 2, 2),
#      ("P4", 1, 3)
# ]
# scheduler = SJFScheduler(tasks)
# scheduler.run_preemptive()  # or run_non_preemptive()
# print_summary(scheduler, mode="Preemptive SJF")


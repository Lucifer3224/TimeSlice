import time

class Priority:

    def __init__(self, simulator, preemptive=False,live=1):
        self.sim = simulator  # instance of ScheduleSimulator
        self.preemptive = preemptive
        self.current_process = None  # Track the running process
        self.live=live

    def run(self):
        completed = set()

        while self.sim.running and len(completed) < len(self.sim.processes):
            ready = [p for p in self.sim.get_ready_processes() if p.pid not in completed]

            if ready:
                # Sort processes by priority (lower value = higher priority)
                ready.sort(key=lambda p: (p.priority, p.arrival_time))

                if self.preemptive:
                    # Check if we need to preempt the current process
                    if self.current_process is None or ready[0].priority < self.current_process.priority:
                        self.current_process = ready[0]

                    p = self.current_process

                    if p.start_time is None:
                        p.start_time = self.sim.time

                    if self.live:
                        time.sleep(1)  # Real-time delay for simulation
                    p.remaining_time -= 1
                    self.sim.timeline.append(p.pid)
                    self.sim.print_status()
                    self.sim.time += 1

                    if p.remaining_time == 0:
                        p.completion_time = self.sim.time
                        completed.add(p.pid)
                        self.current_process = None  # Reset for next process
                else:
                    # Non-preemptive: Pick the highest priority and finish it
                    p = ready[0]
                    if p.start_time is None:
                        p.start_time = self.sim.time

                    while p.remaining_time > 0:
                        if self.live:
                            time.sleep(1)
                        p.remaining_time -= 1
                        self.sim.timeline.append(p.pid)
                        self.sim.print_status()
                        self.sim.time += 1

                    p.completion_time = self.sim.time
                    completed.add(p.pid)

            else:  # No ready process, so the CPU is idle
                if self.live:
                    time.sleep(1)
                self.sim.timeline.append("Idle")
                self.sim.print_status()
                self.sim.time += 1

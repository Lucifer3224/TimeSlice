import matplotlib.pyplot as plt
from matplotlib.patches import Patch

class Proc:
    def __init__(self, pid, at, bt):
        self.pid = pid
        self.at = at
        self.bt = bt
        self.rt = bt
        self.st = None
        self.ct = None

class SJFScheduler:
    def __init__(self, proc_list):
        self.proc_list = proc_list
        self.timeline = []

    def run(self):
        t = 0
        done = []
        p_list = self.proc_list

        while len(done) < len(p_list):
            ready = [p for p in p_list if p.at <= t and p.rt > 0]
            if ready:
                ready.sort(key=lambda p: (p.rt, p.at))
                curr = ready[0]
                if curr.st is None:
                    curr.st = t
                self.timeline += [curr.pid] * curr.rt
                t += curr.rt
                curr.rt = 0
                curr.ct = t
                done.append(curr)
            else:
                self.timeline.append("Idle")
                t += 1

        return self.timeline, p_list

    def _chart_data(self):
        data = []
        tl = self.timeline
        if not tl: return data
        curr = tl[0]
        start = 0
        for i in range(1, len(tl)):
            if tl[i] != curr:
                data.append((curr, start, i - start))
                curr = tl[i]
                start = i
        data.append((curr, start, len(tl) - start))
        return data

    def plot(self, title="Gantt Chart"):
        data = self._chart_data()
        fig, ax = plt.subplots(figsize=(10, 2))
        colors = {}
        pal = plt.cm.tab20.colors
        ci = 0

        for pid, s, d in data:
            if pid not in colors:
                colors[pid] = pal[ci % len(pal)]
                ci += 1
            ax.broken_barh([(s, d)], (10, 9), facecolors=colors[pid])
            ax.text(s + d / 2, 14.5, pid, ha='center', va='center', fontsize=8, color='white')

        ax.set_ylim(5, 25)
        ax.set_xlim(0, len(self.timeline))
        ax.set_xlabel("Time")
        ax.set_yticks([])
        ax.set_title(title)
        legend = [Patch(facecolor=colors[pid], label=pid) for pid in colors]
        ax.legend(handles=legend, loc='upper right', bbox_to_anchor=(1.1, 1))
        plt.tight_layout()
        plt.show()

    def stats(self):
        print("PID  AT  BT  ST  CT  TAT WT")
        for p in self.proc_list:
            tat = p.ct - p.at
            wt = tat - p.bt
            print(f"{p.pid:<4} {p.at:<3} {p.bt:<3} {p.st:<3} {p.ct:<3} {tat:<4} {wt}")

p = [
    Proc("P1", 0, 8),
    Proc("P2", 10, 4),
    Proc("P3", 10, 2),
    Proc("P4", 11, 10)
]

s = SJFScheduler(p)
s.run()
s.plot("SJF Non-Preemptive")
s.stats()

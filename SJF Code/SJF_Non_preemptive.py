import matplotlib.pyplot as plt

class NonPreemptiveSJF:

    def __init__(self, task_list):
        self.task_list = sorted(task_list, key=lambda t: (t[1], t[2]))  
        self.task_count = len(task_list)
        self.finish_times = [0] * self.task_count
        self.delay_times = [0] * self.task_count
        self.response_times = [0] * self.task_count
        self.timeline = []  

    def process_tasks(self):
        current_moment = 0
        pending_tasks = []
        processed_tasks = set()

        while len(processed_tasks) < self.task_count:
            
            for task in self.task_list:
                if task[1] <= current_moment and task[0] not in processed_tasks and task not in pending_tasks:
                    pending_tasks.append(task)

            if pending_tasks:
                
                pending_tasks.sort(key=lambda t: t[2])
                task_id, start_time, duration = pending_tasks.pop(0)
                processed_tasks.add(task_id)

                execution_start = current_moment
                current_moment += duration
                self.finish_times[task_id - 1] = current_moment
                self.response_times[task_id - 1] = current_moment - start_time
                self.delay_times[task_id - 1] = self.response_times[task_id - 1] - duration
                self.timeline.append((task_id, execution_start, current_moment))
            else:
                current_moment += 1  

    def show_results(self):
        avg_delay = sum(self.delay_times) / self.task_count
        avg_response = sum(self.response_times) / self.task_count

        print("Task | Arrival | Duration | Delay | Response")
        print('-------------------------------------------------')
        for i in range(self.task_count):
            tid, arrival, duration = self.task_list[i]
            delay = self.delay_times[i]
            response = self.response_times[i]
            print(f"   {tid:<5}| {arrival:<7} | {duration:<8} | {delay:<5} | {response:<10}")

        print()
        print(f"Average Delay Time: {avg_delay:.2f}")
        print(f"Average Response Time: {avg_response:.2f}")

        self.generate_gantt_chart()

    def generate_gantt_chart(self):
        fig, chart = plt.subplots(figsize=(10, 2))
        for task_id, begin, finish in self.timeline:
            chart.barh(0, finish - begin, left=begin, height=0.5, align='center', label=f'T{task_id}')
            chart.text(begin + (finish - begin) / 2, 0, f'T{task_id}', ha='center', va='center', color='white', fontsize=12, fontweight='bold')

        plt.xlabel("Time")
        plt.yticks([])
        plt.title("Gantt Chart")
        plt.grid(axis='x', linestyle='--')
        plt.show()

if __name__ == '__main__':
    task_data = [(1, 0, 7), (2, 2, 4), (3, 4, 1), (4, 5, 3)]
    scheduler = NonPreemptiveSJF(task_data)
    scheduler.process_tasks()
    scheduler.show_results()

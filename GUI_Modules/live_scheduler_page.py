import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading

from Schedulers.fcfs_scheduler import FCFSScheduler
from Schedulers.priority_scheduler import PriorityScheduler
from Schedulers.round_robin_scheduler import RoundRobinScheduler
from Schedulers.sjf_scheduler import SJFScheduler


class LiveSchedulerPage(tk.Frame):
    def __init__(self, parent, colors, width, height, navigate_home,
                 process_list=None, scheduler_type="FCFS", navigate_to_output=None):
        super().__init__(parent, bg=colors['background'])

        # Store parameters
        self.colors = colors
        self.navigate_home = navigate_home
        self.navigate_to_output = navigate_to_output
        self.width = width
        self.height = height
        self.scheduler_type = scheduler_type

        # ✅ Safely copy the list
        self.process_list = process_list.copy() if isinstance(process_list, list) else []

        # Scheduler state
        self.scheduling_active = False
        self.current_time = 0
        self.scheduler_thread = None
        self.current_process = None
        self.ready_queue = []
        self.waiting_queue = []
        self.completed_processes = []
        self.process_execution_history = []

        # Create a header
        header = tk.Frame(self, bg=colors['button_bg'], height=60)
        header.pack(fill=tk.X, side=tk.TOP)

        back_button = tk.Button(
            header, text="← Back", command=self.confirm_exit,
            bg=colors['button_bg'], fg=colors['button_fg'],
            bd=0, font=("Arial", 12, "bold")
        )
        back_button.pack(side=tk.LEFT, padx=15, pady=10)

        title_label = tk.Label(
            header, text=f"Live {self.scheduler_type} Scheduler", font=("Arial", 16, "bold"),
            bg=colors['button_bg'], fg=colors['button_fg']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Main content - split into two panels
        main_frame = tk.Frame(self, bg=colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Panel - Process Control
        left_frame = tk.Frame(main_frame, bg=colors['background'], width=width // 2 - 30)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Process Input Section
        process_frame = tk.LabelFrame(
            left_frame, text="Add Process", font=("Arial", 12),
            bg=colors['background'], fg=colors['text']
        )
        process_frame.pack(fill=tk.X, pady=10, padx=5)

        # Common fields for all scheduler types
        tk.Label(process_frame, text="Process Name:",
                 bg=colors['background'], fg=colors['text']
                 ).grid(row=0, column=0, sticky='w', padx=5, pady=5)

        self.process_name = tk.Entry(process_frame, width=20, font=("Arial", 12))
        self.process_name.grid(row=0, column=1, padx=5, pady=5)

        row = 1
        tk.Label(process_frame, text="Burst Time (sec):",
                 bg=colors['background'], fg=colors['text']
                 ).grid(row=row, column=0, sticky='w', padx=5, pady=5)

        self.process_duration = tk.Entry(process_frame, width=10, font=("Arial", 12))
        self.process_duration.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        row += 1

        self.arrival_frame = tk.Frame(process_frame, bg=colors['background'])
        self.arrival_frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        tk.Label(self.arrival_frame, text="Arrival Time (sec):",
                 bg=colors['background'], fg=colors['text']
                 ).pack(side=tk.LEFT)

        self.arrival_time = tk.Entry(self.arrival_frame, width=10, font=("Arial", 12))
        self.arrival_time.pack(side=tk.LEFT, padx=5)
        self.arrival_time.insert(0, "0")
        row += 1

        # Additional fields based on scheduler type
        if self.scheduler_type == "Priority":
            self.priority_frame = tk.Frame(process_frame, bg=colors['background'])
            self.priority_frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
            tk.Label(self.priority_frame, text="Priority:",
                     bg=colors['background'], fg=colors['text']
                     ).pack(side=tk.LEFT)

            self.priority_value = tk.Entry(self.priority_frame, width=10, font=("Arial", 12))
            self.priority_value.pack(side=tk.LEFT, padx=5)
            self.priority_value.insert(0, "0")
            row += 1

            # Add preemptive option
            self.preemptive_var = tk.BooleanVar(value=False)
            self.preemptive_frame = tk.Frame(process_frame, bg=colors['background'])
            self.preemptive_frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
            tk.Checkbutton(self.preemptive_frame, text="Preemptive", variable=self.preemptive_var,
                           bg=colors['background'], fg=colors['text']).pack(side=tk.LEFT)
            row += 1

        elif self.scheduler_type == "SJF":
            # Add preemptive option
            self.preemptive_var = tk.BooleanVar(value=False)
            self.preemptive_frame = tk.Frame(process_frame, bg=colors['background'])
            self.preemptive_frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
            tk.Checkbutton(self.preemptive_frame, text="Preemptive", variable=self.preemptive_var,
                           bg=colors['background'], fg=colors['text']).pack(side=tk.LEFT)
            row += 1

        elif self.scheduler_type == "Round Robin":
            self.quantum_frame = tk.Frame(process_frame, bg=colors['background'])
            self.quantum_frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
            tk.Label(self.quantum_frame, text="Time Quantum:",
                     bg=colors['background'], fg=colors['text']
                     ).pack(side=tk.LEFT)

            self.time_quantum = tk.Entry(self.quantum_frame, width=10, font=("Arial", 12))
            self.time_quantum.pack(side=tk.LEFT, padx=5)
            self.time_quantum.insert(0, "2")
            row += 1

        add_button = tk.Button(
            process_frame, text="Add Process",
            bg=colors['button_bg'], fg=colors['button_fg'],
            command=self.add_process
        )
        add_button.grid(row=row, column=0, columnspan=2, pady=10)

        # Process List
        list_frame = tk.LabelFrame(
            left_frame, text="Process Queue", font=("Arial", 12),
            bg=colors['background'], fg=colors['text']
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        list_scroll = tk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.process_listbox = tk.Listbox(
            list_frame, yscrollcommand=list_scroll.set,
            bg=colors['background'], fg=colors['text'], font=("Arial", 12),
            selectbackground=colors['button_bg'], selectforeground=colors['button_fg']
        )
        self.process_listbox.pack(fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.process_listbox.yview)

        delete_button = tk.Button(
            list_frame, text="Delete Selected",
            bg=colors['sign_out_bg'], fg=colors['sign_out_fg'],
            command=self.delete_selected_process
        )
        delete_button.pack(pady=5)

        # Right Panel - Visualization
        right_frame = tk.Frame(main_frame, bg=colors['background'], width=width // 2 - 30)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        right_frame.pack_propagate(False)

        status_frame = tk.LabelFrame(
            right_frame, text="Scheduler Status", font=("Arial", 12),
            bg=colors['background'], fg=colors['text']
        )
        status_frame.pack(fill=tk.X, pady=10, padx=5)

        time_frame = tk.Frame(status_frame, bg=colors['background'])
        time_frame.pack(fill=tk.X, pady=5)
        tk.Label(time_frame, text="Time Elapsed:",
                 bg=colors['background'], fg=colors['text'], font=("Arial", 12)
                 ).pack(side=tk.LEFT, padx=5)

        self.time_label = tk.Label(
            time_frame, text="0s", bg=colors['background'], fg=colors['text'],
            font=("Arial", 12, "bold")
        )
        self.time_label.pack(side=tk.LEFT)

        current_frame = tk.Frame(status_frame, bg=colors['background'])
        current_frame.pack(fill=tk.X, pady=5)
        tk.Label(current_frame, text="Current Process:",
                 bg=colors['background'], fg=colors['text'], font=("Arial", 12)
                 ).pack(side=tk.LEFT, padx=5)

        self.current_process_label = tk.Label(
            current_frame, text="None", bg=colors['background'], fg=colors['text'],
            font=("Arial", 12, "bold")
        )
        self.current_process_label.pack(side=tk.LEFT)

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            status_frame, orient="horizontal", length=width // 2 - 60,
            mode="determinate", variable=self.progress_var
        )
        self.progress.pack(pady=10, padx=5, fill=tk.X)

        # Ready/Waiting queue display
        queue_frame = tk.Frame(status_frame, bg=colors['background'])
        queue_frame.pack(fill=tk.X, pady=5)

        ready_frame = tk.Frame(queue_frame, bg=colors['background'])
        ready_frame.pack(fill=tk.X, pady=5)
        tk.Label(ready_frame, text="Ready Queue:",
                 bg=colors['background'], fg=colors['text'], font=("Arial", 12)
                 ).pack(side=tk.LEFT, padx=5)
        self.ready_queue_label = tk.Label(
            ready_frame, text="Empty", bg=colors['background'],
            fg=colors['text'], font=("Arial", 12)
        )
        self.ready_queue_label.pack(side=tk.LEFT)

        waiting_frame = tk.Frame(queue_frame, bg=colors['background'])
        waiting_frame.pack(fill=tk.X, pady=5)
        tk.Label(waiting_frame, text="Waiting Queue:",
                 bg=colors['background'], fg=colors['text'], font=("Arial", 12)
                 ).pack(side=tk.LEFT, padx=5)
        self.waiting_queue_label = tk.Label(
            waiting_frame, text="Empty", bg=colors['background'],
            fg=colors['text'], font=("Arial", 12)
        )
        self.waiting_queue_label.pack(side=tk.LEFT)

        gantt_frame = tk.LabelFrame(
            right_frame, text="Gantt Chart", font=("Arial", 12),
            bg=colors['background'], fg=colors['text']
        )
        gantt_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        self.canvas = tk.Canvas(gantt_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        control_frame = tk.Frame(self, bg=colors['background'])
        control_frame.pack(fill=tk.X, pady=10, padx=20)

        self.play_button = tk.Button(
            control_frame, text="Start Scheduling",
            bg=colors['button_bg'], fg=colors['button_fg'],
            font=("Arial", 12, "bold"), width=15,
            command=self.toggle_scheduling
        )
        self.play_button.pack(side=tk.LEFT, padx=10)

        reset_button = tk.Button(
            control_frame, text="Reset", bg=colors['sign_out_bg'],
            fg=colors['sign_out_fg'], font=("Arial", 12),
            width=10, command=self.reset_scheduler
        )
        reset_button.pack(side=tk.LEFT, padx=10)

        self.output_button = tk.Button(
            control_frame, text="Go to Output", bg=colors['button_bg'],
            fg=colors['button_fg'], font=("Arial", 12, "bold"),
            width=15, state=tk.DISABLED, command=self.go_to_output
        )
        self.output_button.pack(side=tk.RIGHT, padx=10)

        # Add sample processes

        if not self.process_list:
            self.add_sample_processes()
        else:
            self.populate_from_passed_processes(self.process_list)

    def populate_from_passed_processes(self, process_list):
        for process in self.process_list:
            if self.scheduler_type == "FCFS":
                name, burst, arrival = process
                display_text = f"{name} (Burst: {burst}s, Arrival: {arrival}s)"
            elif self.scheduler_type == "SJF":
                name, burst, arrival, preemptive = process
                display_text = f"{name} (Burst: {burst}s, Arrival: {arrival}s, {'Preemptive' if preemptive else 'Non-Preemptive'})"
            elif self.scheduler_type == "Priority":
                name, burst, arrival, priority, preemptive = process
                display_text = f"{name} (Burst: {burst}s, Arrival: {arrival}s, Priority: {priority}, {'Preemptive' if preemptive else 'Non-Preemptive'})"
            elif self.scheduler_type == "Round Robin":
                name, burst, arrival, quantum = process
                display_text = f"{name} (Burst: {burst}s, Arrival: {arrival}s, Quantum: {quantum}s)"
            else:
                display_text = str(process)

            self.process_listbox.insert(tk.END, display_text)

        self.update_gantt_chart()

        # Progressbar style
        self.style = ttk.Style()
        self.update_progressbar_color()

    def update_queue_labels(self):
        """Refresh the Ready Queue and Waiting Queue label text."""
        if self.ready_queue:
            ready_text = ", ".join(proc[0] for proc in self.ready_queue)
        else:
            ready_text = "Empty"
        if self.waiting_queue:
            waiting_text = ", ".join(proc[0] for proc in self.waiting_queue)
        else:
            waiting_text = "Empty"

        self.ready_queue_label.config(text=ready_text)
        self.waiting_queue_label.config(text=waiting_text)

    def add_sample_processes(self):
        if self.scheduler_type == "FCFS":
            sample_processes = [
                ("Process 1", 5, 0),
                ("Process 2", 3, 1),
                ("Process 3", 8, 2)
            ]
        elif self.scheduler_type == "SJF":
            sample_processes = [
                ("Process 1", 5, 0, False),  # name, burst time, arrival time, preemptive
                ("Process 2", 3, 1, False),
                ("Process 3", 8, 2, False)
            ]
        elif self.scheduler_type == "Priority":
            sample_processes = [
                ("Process 1", 5, 0, 3, False),  # name, burst time, arrival time, priority, preemptive
                ("Process 2", 3, 1, 1, False),
                ("Process 3", 8, 2, 2, False)
            ]
        elif self.scheduler_type == "Round Robin":
            sample_processes = [
                ("Process 1", 5, 0, 2),  # name, burst time, arrival time, quantum
                ("Process 2", 3, 1, 2),
                ("Process 3", 8, 2, 2)
            ]
        else:
            sample_processes = [
                ("Process 1", 5, 0),
                ("Process 2", 3, 1),
                ("Process 3", 8, 2)
            ]

        for process in sample_processes:
            self.process_list.append(process)

            # Format display text based on scheduler type
            if self.scheduler_type == "FCFS":
                name, duration, arrival = process
                display_text = f"{name} (Burst: {duration}s, Arrival: {arrival}s)"
            elif self.scheduler_type == "SJF":
                name, duration, arrival, preemptive = process
                preemptive_text = "Preemptive" if preemptive else "Non-Preemptive"
                display_text = f"{name} (Burst: {duration}s, Arrival: {arrival}s, {preemptive_text})"
            elif self.scheduler_type == "Priority":
                name, duration, arrival, priority, preemptive = process
                preemptive_text = "Preemptive" if preemptive else "Non-Preemptive"
                display_text = f"{name} (Burst: {duration}s, Arrival: {arrival}s, Priority: {priority}, {preemptive_text})"
            elif self.scheduler_type == "Round Robin":
                name, duration, arrival, quantum = process
                display_text = f"{name} (Burst: {duration}s, Arrival: {arrival}s, Quantum: {quantum}s)"
            else:
                name, duration, arrival = process
                display_text = f"{name} (Burst: {duration}s, Arrival: {arrival}s)"

            self.process_listbox.insert(tk.END, display_text)

        self.update_gantt_chart()

    def delete_selected_process(self):
        selected_index = self.process_listbox.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        if 0 <= index < len(self.process_list):
            self.process_list.pop(index)
            self.process_listbox.delete(index)
            self.update_gantt_chart()

    def add_process(self):
        name = self.process_name.get().strip()
        duration_text = self.process_duration.get().strip()
        if not name:
            name = f"Process {len(self.process_list) + 1}"
        try:
            duration = int(duration_text)
            if duration <= 0:
                raise ValueError("Duration must be positive")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for burst time")
            return

        if self.scheduling_active:
            arrival_time = self.current_time
        else:
            try:
                arrival_time = int(self.arrival_time.get().strip())
                if arrival_time < 0:
                    raise ValueError("Arrival time must be non-negative")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid non-negative number for arrival time")
                return

        # Create process tuple based on scheduler type
        if self.scheduler_type == "FCFS":
            process = (name, duration, arrival_time)
        elif self.scheduler_type == "SJF":
            preemptive = getattr(self, 'preemptive_var', tk.BooleanVar()).get()
            process = (name, duration, arrival_time, preemptive)
        elif self.scheduler_type == "Priority":
            try:
                priority = int(self.priority_value.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for priority")
                return
            preemptive = getattr(self, 'preemptive_var', tk.BooleanVar()).get()
            process = (name, duration, arrival_time, priority, preemptive)
        elif self.scheduler_type == "Round Robin":
            try:
                quantum = int(self.time_quantum.get().strip())
                if quantum <= 0:
                    raise ValueError("Time quantum must be positive")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid positive number for time quantum")
                return
            process = (name, duration, arrival_time, quantum)
        else:
            process = (name, duration, arrival_time)

        self.process_list.append(process)

        # Format the display in the listbox differently based on scheduler type
        if self.scheduler_type == "FCFS":
            display_text = f"{name} (Burst: {duration}s, Arrival: {arrival_time}s)"
        elif self.scheduler_type == "SJF":
            preemptive = getattr(self, 'preemptive_var', tk.BooleanVar()).get()
            preemptive_text = "Preemptive" if preemptive else "Non-Preemptive"
            display_text = f"{name} (Burst: {duration}s, Arrival: {arrival_time}s, {preemptive_text})"
        elif self.scheduler_type == "Priority":
            priority = int(self.priority_value.get().strip())
            preemptive = getattr(self, 'preemptive_var', tk.BooleanVar()).get()
            preemptive_text = "Preemptive" if preemptive else "Non-Preemptive"
            display_text = f"{name} (Burst: {duration}s, Arrival: {arrival_time}s, Priority: {priority}, {preemptive_text})"
        elif self.scheduler_type == "Round Robin":
            quantum = int(self.time_quantum.get().strip())
            display_text = f"{name} (Burst: {duration}s, Arrival: {arrival_time}s, Quantum: {quantum}s)"
        else:
            display_text = f"{name} (Burst: {duration}s, Arrival: {arrival_time}s)"

        self.process_listbox.insert(tk.END, display_text)

        # Clear inputs
        self.process_name.delete(0, tk.END)
        self.process_duration.delete(0, tk.END)
        self.arrival_time.delete(0, tk.END)
        self.arrival_time.insert(0, str(self.current_time if self.scheduling_active else 0))

        # Clear additional fields based on scheduler type
        if self.scheduler_type == "Priority" and hasattr(self, 'priority_value'):
            self.priority_value.delete(0, tk.END)
            self.priority_value.insert(0, "0")
        elif self.scheduler_type == "Round Robin" and hasattr(self, 'time_quantum'):
            self.time_quantum.delete(0, tk.END)
            self.time_quantum.insert(0, "2")

        self.update_gantt_chart()

        if self.scheduling_active:
            self.restart_scheduler()

    def restart_scheduler(self):
        self.restarting = True
        self.scheduling_active = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(0.1)
        self.restarting = False
        self.scheduling_active = True
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def update_gantt_chart(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width() or self.width // 2 - 60
        canvas_height = self.canvas.winfo_height() or 200
        margin = 70

        if self.process_execution_history:
            total_time = max(self.current_time, max(end for _, _, end, _ in self.process_execution_history))
        else:
            total_time = max(1, sum(duration for _, duration, *_ in self.process_list))

        time_scale = (canvas_width - margin - 20) / max(1, total_time)

        # Time axis
        self.canvas.create_line(margin, canvas_height - 30, canvas_width - 10, canvas_height - 30, width=2)
        self.canvas.create_text(
            canvas_width // 2, canvas_height - 10,
            text="Time (seconds)", font=("Arial", 10, "bold")
        )
        tick_interval = max(1, total_time // min(10, total_time))
        for t in range(0, total_time + 1, tick_interval):
            x = margin + t * time_scale
            self.canvas.create_line(x, canvas_height - 30, x, canvas_height - 25, width=2)
            self.canvas.create_text(x, canvas_height - 15, text=str(t), font=("Arial", 8))

        self.canvas.create_text(margin // 2, 10, text="Process", font=("Arial", 10, "bold"))

        # Assign colors
        process_colors = [
            "#4CAF50", "#2196F3", "#FFC107", "#9C27B0", "#F44336",
            "#009688", "#795548", "#607D8B", "#E91E63", "#673AB7"
        ]
        unique_processes = set()
        for entry in self.process_execution_history:
            unique_processes.add(entry[0])
        for proc in self.process_list:
            unique_processes.add(proc[0])
        # Sort so color assignment is stable
        process_color_map = {
            proc: process_colors[i % len(process_colors)]
            for i, proc in enumerate(sorted(unique_processes))
        }

        # If nothing has run yet, just draw process names without bars
        if not self.process_execution_history:
            y_pos = 30
            bar_height = 25
            for i, process in enumerate(sorted([(p[0], i) for i, p in enumerate(self.process_list)])):
                name, orig_idx = process
                y = y_pos + i * (bar_height + 10)
                self.canvas.create_text(
                    margin - 5, y + bar_height / 2,
                    text=name, anchor="e", font=("Arial", 10)
                )
                # Just draw a thin line to indicate the timeline
                # self.canvas.create_line(
                #   margin, y + bar_height / 2,
                #          canvas_width - 20, y + bar_height / 2,
                # dash=(2, 4), fill="#CCCCCC"
                # )
        else:
            # Group segments by process
            process_timelines = {}
            for name, start, end, status in self.process_execution_history:
                process_timelines.setdefault(name, []).append((start, end, status))

            y_pos = 30
            bar_height = 25
            # Sort by name for consistent vertical ordering
            for i, (name, timeline) in enumerate(sorted(process_timelines.items())):
                color = process_color_map.get(name, "#CCCCCC")
                y = y_pos + i * (bar_height + 10)
                self.canvas.create_text(
                    margin - 5, y + bar_height / 2,
                    text=name, anchor="e", font=("Arial", 10)
                )
                for start, end, status in timeline:
                    x1 = margin + start * time_scale
                    x2 = margin + end * time_scale
                    # "running" gets color, "ready" is a lighter fill
                    fill_color = color if status == "running" else "#EEEEEE"
                    self.canvas.create_rectangle(
                        x1, y, x2, y + bar_height, fill=fill_color, outline="black"
                    )
                    if (x2 - x1) > 30:
                        duration = end - start
                        self.canvas.create_text(
                            (x1 + x2) / 2, y + bar_height / 2,
                            text=f"{duration}s", font=("Arial", 9), fill="black"
                        )

        # Current-time marker
        if self.scheduling_active and self.current_time > 0:
            current_x = margin + self.current_time * time_scale
            self.canvas.create_line(
                current_x, 10, current_x, canvas_height - 40,
                width=2, fill="red", dash=(4, 2), tags="time_marker"
            )
            self.canvas.create_text(
                current_x, 5, text=f"Current: {self.current_time}s",
                fill="red", font=("Arial", 8, "bold"), tags="time_marker"
            )

    def update_progressbar_color(self):
        pass

    def toggle_scheduling(self):
        if not self.scheduling_active:
            if not self.process_list:
                messagebox.showinfo("No Processes", "Please add at least one process before starting")
                return
            self.scheduling_active = True
            self.play_button.config(text="Pause Scheduling")
            self.arrival_frame.grid_forget()
            self.scheduler_thread = threading.Thread(target=self.run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
        else:
            self.scheduling_active = False
            self.play_button.config(text="Resume Scheduling")

    def run_scheduler(self):
        """Run the scheduler with second-by-second partial updates."""
        if not hasattr(self, 'restarting') or not self.restarting:
            self.current_time = 0
            self.process_execution_history = []
            self.completed_processes = []

        # Initialize the appropriate scheduler based on the scheduler type
        if self.scheduler_type == "FCFS":
            scheduler = FCFSScheduler(self.process_list)
        elif self.scheduler_type == "SJF":
            scheduler = SJFScheduler(self.process_list)
        elif self.scheduler_type == "Priority":
            scheduler = PriorityScheduler(self.process_list)
        elif self.scheduler_type == "Round Robin":
            scheduler = RoundRobinScheduler(self.process_list)
        else:
            # Default to FCFS
            scheduler = FCFSScheduler(self.process_list)

        self.ready_queue = []  # For UI display only
        self.waiting_queue = []  # For UI display only
        self.current_process = None
        remaining_time = 0
        time_quantum = 0  # For Round Robin

        while self.scheduling_active:
            # Update the queues with newly arrived processes
            newly_arrived = scheduler.update_queues(self.current_time)

            # Update UI display queues
            self.waiting_queue = scheduler.waiting_queue
            self.ready_queue = scheduler.ready_queue
            self.update_queue_labels()

            # Record "ready" state for newly arrived processes
            for proc in newly_arrived:
                self.process_execution_history.append((proc[0], self.current_time, self.current_time, "ready"))

            # Process selection based on scheduling algorithm
            if not self.current_process:
                if self.scheduler_type == "FCFS":
                    self.current_process, remaining_time = scheduler.run(self.current_time)

                elif self.scheduler_type == "SJF":
                    # Check if we're using preemptive SJF
                    is_preemptive = len(self.process_list[0]) > 3 and self.process_list[0][3]
                    if is_preemptive:
                        self.current_process, remaining_time, _ = scheduler.run_preemptive(self.current_time)
                    else:
                        self.current_process, remaining_time = scheduler.run_non_preemptive(self.current_time)

                elif self.scheduler_type == "Priority":
                    # Check if we're using preemptive Priority
                    is_preemptive = len(self.process_list[0]) > 4 and self.process_list[0][4]
                    if is_preemptive:
                        self.current_process, remaining_time, _ = scheduler.run_preemptive(self.current_time)
                    else:
                        self.current_process, remaining_time = scheduler.run_non_preemptive(self.current_time)

                elif self.scheduler_type == "Round Robin":
                    process_info = scheduler.run(self.current_time)
                    if process_info[0]:  # If a process was selected
                        self.current_process, remaining_time, time_quantum = process_info[0]

                # Start execution
                if self.current_process:
                    self.current_process_label.config(text=self.current_process[0])
                    # Start "running" segment
                    self.process_execution_history.append(
                        (self.current_process[0], self.current_time,
                         self.current_time + (
                             time_quantum if self.scheduler_type == "Round Robin" and remaining_time > time_quantum else remaining_time),
                         "running")
                    )

            # Execute current process for one second
            if self.current_process:
                time.sleep(1)
                self.current_time += 1
                remaining_time -= 1

                if self.scheduler_type == "Round Robin" and time_quantum > 0:
                    time_quantum -= 1

                self.time_label.config(text=f"{self.current_time}s")

                # Preemption checks for SJF and Priority
                preempted = False

                # Check for preemption based on scheduler type
                if self.scheduler_type == "SJF" and len(self.current_process) > 3 and self.current_process[3]:
                    self.current_process, remaining_time, preempted = scheduler.run_preemptive(
                        self.current_time, self.current_process, remaining_time
                    )

                    if preempted:
                        # Update execution history end time
                        self.update_execution_history_end_time(
                            self.process_execution_history[-1][0], self.current_time
                        )
                        self.current_process_label.config(text=self.current_process[0])
                        # Start new "running" segment
                        self.process_execution_history.append(
                            (self.current_process[0], self.current_time, self.current_time + remaining_time, "running")
                        )

                # Preemptive Priority check
                elif self.scheduler_type == "Priority" and len(self.current_process) > 4 and self.current_process[4]:
                    self.current_process, remaining_time, preempted = scheduler.run_preemptive(
                        self.current_time, self.current_process, remaining_time
                    )

                    if preempted:
                        # Update execution history end time
                        self.update_execution_history_end_time(
                            self.process_execution_history[-1][0], self.current_time
                        )
                        self.current_process_label.config(text=self.current_process[0])
                        # Start new "running" segment
                        self.process_execution_history.append(
                            (self.current_process[0], self.current_time, self.current_time + remaining_time, "running")
                        )

                # Round Robin: Time quantum expired
                elif self.scheduler_type == "Round Robin" and time_quantum == 0 and remaining_time > 0:
                    process_info = scheduler.run(
                        self.current_time, self.current_process, remaining_time, time_quantum
                    )

                    if process_info[1]:  # If this is a new process
                        # Update execution history end time
                        self.update_execution_history_end_time(self.current_process[0], self.current_time)

                        # Get the selected process info
                        self.current_process, remaining_time, time_quantum = process_info[0]

                        if self.current_process:
                            self.current_process_label.config(text=self.current_process[0])
                            # Start new "running" segment  
                            self.process_execution_history.append(
                                (self.current_process[0], self.current_time,
                                 self.current_time + (
                                     time_quantum if remaining_time > time_quantum else remaining_time),
                                 "running")
                            )
                        else:
                            self.current_process_label.config(text="None")

                # Update progress bar
                if not preempted:
                    if remaining_time > 0:
                        if self.scheduler_type == "Round Robin":
                            original_quantum = time_quantum + 1 if time_quantum > 0 else 2  # Estimate original quantum
                            progress = original_quantum - time_quantum
                            self.progress_var.set((progress / original_quantum) * 100)
                        else:
                            total = self.current_process[1]  # Original burst time
                            progress = total - remaining_time
                            self.progress_var.set((progress / total) * 100)
                    else:
                        self.progress_var.set(100)

                self.update_gantt_chart()

                # Process completion check
                if remaining_time <= 0 and not preempted:
                    # Update execution history end time
                    self.update_execution_history_end_time(self.current_process[0], self.current_time)
                    self.completed_processes.append(self.current_process)
                    self.current_process_label.config(text="None")
                    self.current_process = None
            else:
                # No process running => idle
                time.sleep(1)
                self.current_time += 1
                self.time_label.config(text=f"{self.current_time}s")
                self.update_gantt_chart()

            # Check if we're done scheduling
            if scheduler.is_done() and not self.current_process:
                break

        self.scheduling_active = False
        self.play_button.config(text="Start Scheduling")
        self.output_button.config(state=tk.NORMAL)

    def update_execution_history_end_time(self, process_name, end_time):
        """Update the end time of the most recent execution segment for a process"""
        for i in range(len(self.process_execution_history) - 1, -1, -1):
            entry = self.process_execution_history[i]
            if entry[0] == process_name and entry[3] == "running":
                self.process_execution_history[i] = (entry[0], entry[1], end_time, "running")
                break

    def reset_scheduler(self):
        self.scheduling_active = False
        self.current_time = 0
        self.process_list.clear()
        self.process_listbox.delete(0, tk.END)
        self.ready_queue.clear()
        self.waiting_queue.clear()
        self.process_execution_history.clear()
        self.completed_processes.clear()
        self.time_label.config(text="0s")
        self.current_process_label.config(text="None")
        self.progress_var.set(0)
        self.canvas.delete("all")
        self.output_button.config(state=tk.DISABLED)
        self.add_sample_processes()

    def go_to_output(self):
        if self.navigate_to_output:
            # Pass the necessary data to the output page
            self.navigate_to_output(
                completed_processes=self.completed_processes,
                process_execution_history=self.process_execution_history
            )

    def confirm_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.scheduling_active = False
            if self.navigate_home:
                self.navigate_home()
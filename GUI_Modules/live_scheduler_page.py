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
                 process_list=None, scheduler_type="FCFS", flag_live_scheduler=0 ,navigate_to_output=None):
        super().__init__(parent, bg=colors['background'])

        # Store parameters
        self.flag_live_scheduler=flag_live_scheduler 
        self.colors = colors
        self.navigate_home = navigate_home
        self.navigate_to_output = navigate_to_output
        self.width = width
        self.height = height
        self.scheduler_type = scheduler_type

        # ✅ Safely copy the list and save as original_process_list
        self.original_process_list = process_list.copy() if isinstance(process_list, list) else []
        self.process_list = self.original_process_list.copy()  # Working copy

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

        elif self.scheduler_type == "Round Robin":
            pass  # No specific input needed here anymore for RR

        # Remove the primitive/non-primitive check button and enforce consistent process types.
        if self.scheduler_type in ["SJF", "Priority"]:
            self.preemptive_var = tk.BooleanVar(value=self.process_list[0][3] if self.process_list else False)

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

        # Create a container for the Gantt chart with scrollbars
        gantt_container = tk.Frame(gantt_frame, bg=colors['background'])
        gantt_container.pack(fill=tk.BOTH, expand=True)
        
        # Add horizontal and vertical scrollbars for the Gantt chart
        gantt_h_scroll = tk.Scrollbar(gantt_container, orient="horizontal")
        gantt_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        gantt_v_scroll = tk.Scrollbar(gantt_container, orient="vertical")
        gantt_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the canvas with scroll capability
        self.canvas = tk.Canvas(
            gantt_container, 
            bg="white", 
            highlightthickness=0,
            xscrollcommand=gantt_h_scroll.set,
            yscrollcommand=gantt_v_scroll.set
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure the scrollbars to work with the canvas
        gantt_h_scroll.config(command=self.canvas.xview)
        gantt_v_scroll.config(command=self.canvas.yview)

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
        self.process_list = process_list.copy() if isinstance(process_list, list) else []
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

    # Fix crash when adding a process while scheduling and ensure correct arrival time when paused.
    def add_process(self):
        # Validate process name
        name = self.process_name.get().strip()
        if not name:
            name = f"Process {len(self.process_list) + 1}"
        
        # Validate burst time - must be positive integer
        duration_text = self.process_duration.get().strip()
        try:
            # Check if it's a valid integer
            if not duration_text.isdigit():
                raise ValueError("Burst time must be a positive integer")
            
            duration = int(duration_text)
            if duration <= 0:
                raise ValueError("Burst time must be positive")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        # Set arrival time based on current state
        if self.scheduling_active:
            arrival_time = self.current_time
        else:
            try:
                arrival_text = self.arrival_time.get().strip()
                # Check if it's a valid non-negative integer
                if not arrival_text.isdigit() and arrival_text != '0':
                    raise ValueError("Arrival time must be a non-negative integer")
                
                arrival_time = int(arrival_text)
                if arrival_time < 0:
                    raise ValueError("Arrival time cannot be negative")
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))
                return

        # Create process tuple based on scheduler type
        if self.scheduler_type == "FCFS":
            process = (name, duration, arrival_time)
        elif self.scheduler_type == "SJF":
            # Use the preemptive value from existing processes for consistency
            preemptive = False
            if self.process_list and len(self.process_list[0]) > 3:
                preemptive = self.process_list[0][3]
            process = (name, duration, arrival_time, preemptive)
        elif self.scheduler_type == "Priority":
            try:
                priority_text = self.priority_value.get().strip()
                # Check if it's a valid integer (can be negative for priority)
                if not priority_text.isdigit() and not (priority_text.startswith('-') and priority_text[1:].isdigit()):
                    raise ValueError("Priority must be an integer")
                
                priority = int(priority_text)
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))
                return
            
            # Use the preemptive value from existing processes for consistency
            preemptive = False
            if self.process_list and len(self.process_list[0]) > 4:
                preemptive = self.process_list[0][4]
            process = (name, duration, arrival_time, priority, preemptive)
        elif self.scheduler_type == "Round Robin":
            # Determine the quantum to use automatically from original processes
            default_quantum = 2  # Default value if no original processes exist
            quantum_to_use = default_quantum

            # Try to get the quantum from the original processes
            if self.original_process_list:
                try:
                    # Assuming the 4th element (index 3) is the quantum for RR
                    if len(self.original_process_list[0]) > 3:
                        original_quantum = int(self.original_process_list[0][3])
                        # Validate fetched quantum is positive
                        if original_quantum > 0:
                            quantum_to_use = original_quantum
                        else:
                            print(f"Warning: Original quantum ({original_quantum}) is not positive. Using default {default_quantum}.")
                    else:
                        print(f"Warning: Original process tuple for RR doesn't have quantum info. Using default {default_quantum}.")
                except (IndexError, ValueError, TypeError) as e:
                    print(f"Error retrieving original quantum: {e}. Using default {default_quantum}.")

            # Create the process tuple with the determined quantum
            process = (name, duration, arrival_time, quantum_to_use)
        else:
            process = (name, duration, arrival_time)

        # Add to process_list
        self.process_list.append(process)
        
        # Update process_details dictionary so progress bar works for the new process
        if hasattr(self, 'process_details'):
            self.process_details[name] = {"burst": duration, "arrival": arrival_time}

        # Format the display in the listbox differently based on scheduler type
        if self.scheduler_type == "FCFS":
            display_text = f"{name} (Burst: {duration}s, Arrival: {arrival_time}s)"
        elif self.scheduler_type == "SJF":
            preemptive = process[3]  # Use the value from the process tuple
            preemptive_text = "Preemptive" if preemptive else "Non-Preemptive"
            display_text = f"{name} (Burst: {duration}s, Arrival: {arrival_time}s, {preemptive_text})"
        elif self.scheduler_type == "Priority":
            priority = process[3]  # Use the value from the process tuple
            preemptive = process[4]  # Use the value from the process tuple
            preemptive_text = "Preemptive" if preemptive else "Non-Preemptive"
            display_text = f"{name} (Burst: {duration}s, Arrival: {arrival_time}s, Priority: {priority}, {preemptive_text})"
        elif self.scheduler_type == "Round Robin":
            quantum = process[3]  # Use the value from the process tuple
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

        self.update_gantt_chart()

        if self.scheduling_active:
            self.restart_scheduler()

    def restart_scheduler(self):
        """Safely restart the scheduler after adding a new process during runtime."""
        self.restarting = True
        
        # Set flag to stop the current scheduler thread
        self.scheduling_active = False
        
        # Wait for scheduler thread to terminate safely
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            try:
                self.scheduler_thread.join(0.5)  # Increased timeout for safe termination
            except Exception as e:
                print(f"Thread join error: {e}")
                # Continue anyway - we'll create a new thread
                
        # Keep current time and execution history
        # But reset other states that might be inconsistent
        if hasattr(self, 'ready_queue'):
            self.ready_queue = []
        if hasattr(self, 'waiting_queue'):
            self.waiting_queue = []
            
        # Set flags to start a new scheduler
        self.restarting = False
        self.scheduling_active = True
        
        # Start a new scheduler thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def update_gantt_chart(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width() or self.width // 2 - 60
        canvas_height = self.canvas.winfo_height() or 200
        margin = 70

        # Count unique processes to calculate required height
        unique_processes = set()
        for entry in self.process_execution_history:
            unique_processes.add(entry[0])
        for proc in self.process_list:
            unique_processes.add(proc[0])
        
        # Calculate the required height based on process count
        bar_height = 25
        bar_spacing = 10
        y_pos = 30
        required_height = y_pos + len(unique_processes) * (bar_height + bar_spacing) + 50  # +50 for time axis

        if self.process_execution_history:
            total_time = max(self.current_time, max(end for _, _, end, _ in self.process_execution_history))
        else:
            total_time = max(1, sum(duration for _, duration, *_ in self.process_list))

        time_scale = (canvas_width - margin - 20) / max(1, total_time)
        
        # Calculate needed width for the timeline
        required_width = margin + (total_time * time_scale) + 50
        
        # Set scroll region to accommodate all processes and timeline
        self.canvas.configure(scrollregion=(0, 0, max(canvas_width, required_width), max(canvas_height, required_height)))

        # Time axis
        self.canvas.create_line(margin, max(canvas_height, required_height) - 30, max(canvas_width, required_width) - 10, max(canvas_height, required_height) - 30, width=2)
        self.canvas.create_text(
            (margin + max(canvas_width, required_width) - 10) // 2, max(canvas_height, required_height) - 10,
            text="Time (seconds)", font=("Arial", 10, "bold")
        )
        tick_interval = max(1, total_time // min(10, total_time))
        for t in range(0, total_time + 1, tick_interval):
            x = margin + t * time_scale
            self.canvas.create_line(x, max(canvas_height, required_height) - 30, x, max(canvas_height, required_height) - 25, width=2)
            self.canvas.create_text(x, max(canvas_height, required_height) - 15, text=str(t), font=("Arial", 8))

        self.canvas.create_text(margin // 2, 10, text="Process", font=("Arial", 10, "bold"))

        # Assign colors
        process_colors = [
            "#4CAF50", "#2196F3", "#FFC107", "#9C27B0", "#F44336",
            "#009688", "#795548", "#607D8B", "#E91E63", "#673AB7",
            "#3F51B5", "#FF9800", "#CDDC39", "#8BC34A", "#00BCD4"  # Added more colors
        ]
        # Sort so color assignment is stable
        sorted_processes = sorted(unique_processes)
        process_color_map = {
            proc: process_colors[i % len(process_colors)]
            for i, proc in enumerate(sorted_processes)
        }

        # If nothing has run yet, just draw process names without bars
        if not self.process_execution_history:
            for i, process_name in enumerate(sorted_processes):
                y = y_pos + i * (bar_height + bar_spacing)
                self.canvas.create_text(
                    margin - 5, y + bar_height / 2,
                    text=process_name, anchor="e", font=("Arial", 10)
                )
        else:
            # Group segments by process
            process_timelines = {}
            for name, start, end, status in self.process_execution_history:
                process_timelines.setdefault(name, []).append((start, end, status))

            # Sort by name for consistent vertical ordering
            for i, name in enumerate(sorted_processes):
                if name not in process_timelines:
                    continue
                    
                color = process_color_map.get(name, "#CCCCCC")
                y = y_pos + i * (bar_height + bar_spacing)
                self.canvas.create_text(
                    margin - 5, y + bar_height / 2,
                    text=name, anchor="e", font=("Arial", 10)
                )
                
                timeline = process_timelines[name]
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
                current_x, 10, current_x, max(canvas_height, required_height) - 40,
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
            # Ensure original process list is used for lookups if needed
            self.process_details = {p[0]: {"burst": p[1], "arrival": p[2]} for p in self.original_process_list}


        # Initialize the appropriate scheduler
        # Pass a copy of the original list of tuples
        scheduler_process_list = self.process_list.copy()
        if self.scheduler_type == "FCFS":
            scheduler = FCFSScheduler(scheduler_process_list)
        elif self.scheduler_type == "SJF":
            scheduler = SJFScheduler(scheduler_process_list)
        elif self.scheduler_type == "Priority":
            scheduler = PriorityScheduler(scheduler_process_list)
        elif self.scheduler_type == "Round Robin":
            # Initialize RR scheduler using the determined quantum from the first original process if available
            default_quantum = 2
            quantum_to_use = default_quantum
            if self.original_process_list:
                try:
                    if len(self.original_process_list[0]) > 3:
                        original_quantum = int(self.original_process_list[0][3])
                        if original_quantum > 0:
                            quantum_to_use = original_quantum
                except (IndexError, ValueError, TypeError):
                    pass  # Use default if error

            scheduler = RoundRobinScheduler(scheduler_process_list, quantum_to_use)
        else:
            scheduler = FCFSScheduler(scheduler_process_list)

        self.ready_queue = []  # For UI display only
        self.waiting_queue = [] # For UI display only
        self.current_process = None # Tuple of the currently running process
        remaining_time = 0      # Remaining time for self.current_process
        time_quantum_left = 0 # For Round Robin

        last_process_name = None # Track changes for history update

        while self.scheduling_active:
            # 1. Update queues based on current_time (move arrived to ready)
            newly_arrived = scheduler.update_queues(self.current_time)
            self.waiting_queue = scheduler.waiting_queue # Update UI state
            self.ready_queue = scheduler.ready_queue   # Update UI state
            self.update_queue_labels()

            # 2. Determine scheduling mode (preemptive or non-preemptive)
            #    This relies on the assumption that all processes have the same flag.
            #    A more robust design might set this based on initial UI selection.
            preemptive_mode = False
            if self.scheduler_type == "SJF" and self.process_list:
                if len(self.process_list[0]) > 3:
                    preemptive_mode = self.process_list[0][3]
            elif self.scheduler_type == "Priority" and self.process_list:
                 if len(self.process_list[0]) > 4:
                     # Assuming PriorityScheduler also uses the last element for preemptive flag
                     preemptive_mode = self.process_list[0][4]

            # 3. Decide which process should run NOW based on mode
            process_to_run = None
            time_for_process = 0 # This is the REMAINING time for the selected process
            preempted_flag = False # Tracks if preemption occurred *this tick*

            if preemptive_mode:
                # Call preemptive logic (SRTF for SJF, Preemptive Priority)
                # Assumes scheduler has a 'run_preemptive' method if mode is preemptive
                if hasattr(scheduler, 'run_preemptive'):
                    process_to_run, time_for_process, preempted_flag = scheduler.run_preemptive(
                        self.current_time, self.current_process, remaining_time
                    )
                else:
                    # Fallback or error if preemptive mode selected but method missing
                    print(f"Warning: Preemptive mode selected for {self.scheduler_type}, but run_preemptive not found.")
                    # Defaulting to non-preemptive behavior for this tick
                    if not self.current_process:
                         if hasattr(scheduler, 'run_non_preemptive'):
                              process_to_run, time_for_process = scheduler.run_non_preemptive(self.current_time)
                         elif self.scheduler_type == "FCFS": # FCFS only has run()
                              process_to_run, time_for_process = scheduler.run(self.current_time)
                    else:
                         process_to_run = self.current_process
                         time_for_process = remaining_time

            elif self.scheduler_type == "Round Robin":
                 # RR logic needs current process, remaining time, and quantum slice
                 process_to_run, time_for_process, time_quantum_left, preempted_flag = scheduler.run(
                     self.current_time, self.current_process, remaining_time, time_quantum_left
                 )

            else: # Non-preemptive modes (FCFS, non-preemptive SJF/Priority)
                if not self.current_process: # Only select new if CPU is idle
                    if self.scheduler_type == "FCFS":
                         process_to_run, time_for_process = scheduler.run(self.current_time)
                    elif self.scheduler_type in ["SJF", "Priority"]:
                         # Ensure non-preemptive method exists
                         if hasattr(scheduler, 'run_non_preemptive'):
                              process_to_run, time_for_process = scheduler.run_non_preemptive(self.current_time)
                         else:
                              print(f"Warning: Non-preemptive method missing for {self.scheduler_type}")
                              process_to_run = None
                              time_for_process = 0
                else:
                    # Non-preemptive: current process continues until done
                    process_to_run = self.current_process
                    time_for_process = remaining_time # Continue with the current remaining time

            # --- State Update based on Decision ---
            current_process_name = process_to_run[0] if process_to_run else None

            # If the running process changed (or started/stopped)
            if current_process_name != last_process_name:
                # If a process was running previously, update its history end time
                if last_process_name and self.process_execution_history:
                    self.update_execution_history_end_time(last_process_name, self.current_time)

                # If a new process is starting/resuming
                if process_to_run:
                    self.current_process = process_to_run
                    # CRITICAL: Use the remaining time returned by the scheduler
                    remaining_time = time_for_process
                    self.current_process_label.config(text=current_process_name)
                    # Add new segment to history
                    # Estimate end time for now, will be updated if preempted or finished
                    estimated_end = self.current_time + remaining_time
                    self.process_execution_history.append(
                        (current_process_name, self.current_time, estimated_end, "running")
                    )
                else:
                    # No process is running now (idle or finished)
                    self.current_process = None
                    remaining_time = 0
                    self.current_process_label.config(text="None")
                    self.progress_var.set(0)

                last_process_name = current_process_name
            # No need for 'elif process_to_run:' here, as remaining_time is handled
            # when the process is selected/continues.

            # --- Execute for one time unit --- 
            if self.current_process:
                # Check if still active before sleeping/advancing time
                if not self.scheduling_active: break
                time.sleep(0.5) # Reduced sleep for faster simulation

                # Advance time and decrement remaining time *for the current process*
                self.current_time += 1
                remaining_time -= 1
                if self.scheduler_type == "Round Robin":
                    time_quantum_left -= 1

                self.time_label.config(text=f"{self.current_time}s")

                # Update progress bar
                original_burst = self.process_details.get(self.current_process[0], {}).get("burst", 0)
                if original_burst > 0:
                    # Calculate progress based on how much time is left
                    progress_done = original_burst - remaining_time
                    self.progress_var.set((progress_done / original_burst) * 100)
                else:
                    self.progress_var.set(0)

                # Check for completion AFTER executing and decrementing
                if remaining_time <= 0:
                    self.update_execution_history_end_time(self.current_process[0], self.current_time)
                    # Find the completed process tuple to add (using original details)
                    completed_tuple = next((p for p in self.original_process_list if p[0] == self.current_process[0]), None)
                    # If the process is not in the original list, it must be a newly added process, so use the current process
                    if not completed_tuple:
                        completed_tuple = self.current_process
                    
                    # Add to completed processes
                    if completed_tuple:
                        self.completed_processes.append(completed_tuple)

                    # Mark as finished for the next loop iteration's decision phase
                    self.current_process = None
                    remaining_time = 0
                    last_process_name = None # Reset last process tracker
                    self.current_process_label.config(text="None")
                    self.progress_var.set(100) # Show 100% briefly

            else:
                # No process running => idle tick
                # Only advance time if there are still processes waiting or ready
                if not scheduler.is_done():
                     # Check if still active before sleeping/advancing time
                    if not self.scheduling_active: break
                    time.sleep(0.5) # Reduced sleep
                    self.current_time += 1
                    self.time_label.config(text=f"{self.current_time}s")
                else:
                    # If scheduler is done and no process running, break immediately
                    if not self.current_process:
                         break

            # Update Gantt chart (always update to show time marker)
            # Ensure GUI updates happen on the main thread if needed (Tkinter is usually main thread only)
            # self.after(0, self.update_gantt_chart) # Example if needed
            self.update_gantt_chart()

            # Check for overall completion
            # Need to check is_done() AND if a process is still running its last tick
            if scheduler.is_done() and not self.current_process:
                break # Exit the loop

        # --- End of Loop --- 
        self.scheduling_active = False
        self.play_button.config(text="Start Scheduling")
        self.output_button.config(state=tk.NORMAL)
        
        # Reset arrival time field to 0 after scheduling finishes
        if hasattr(self, 'arrival_time'):
            self.arrival_time.delete(0, tk.END)
            self.arrival_time.insert(0, "0")
            
        # Final Gantt chart update to ensure completion is shown
        self.update_gantt_chart()

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
        self.process_list = self.original_process_list.copy()  # Restore from original
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
        
        # Populate listbox with original processes instead of adding sample processes
        if self.original_process_list:
            self.populate_from_passed_processes(self.original_process_list)
        else:
            # Only add sample processes if no original processes were provided
            self.add_sample_processes()

    def go_to_output(self):
        if self.navigate_to_output:
            # Pass the necessary data to the output page, including the current process list
            self.navigate_to_output(
                completed_processes=self.completed_processes,
                process_execution_history=self.process_execution_history,
                process_list=self.process_list.copy(),  # Pass current process list
                scheduler_type=self.scheduler_type
            )

    def confirm_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.scheduling_active = False
            if hasattr(self, 'navigate_to_scheduler') and self.navigate_to_scheduler:
                self.navigate_to_scheduler(self.process_list, self.scheduler_type)
            else:
                if self.navigate_home:
                    self.navigate_home()
import tkinter as tk
from tkinter import ttk
import math


class OutputPage(tk.Frame):
    def __init__(self, parent, colors, width, height, navigate_home, navigate_to_scheduler,
                 completed_processes=None, process_execution_history=None, scheduler_type="FCFS"):
        super().__init__(parent, bg=colors['background'])

        # Store parameters
        self.colors = colors
        self.navigate_home = navigate_home
        self.navigate_to_scheduler = navigate_to_scheduler
        self.width = width
        self.height = height
        self.completed_processes = completed_processes or []
        self.process_execution_history = process_execution_history or []
        self.scheduler_type = scheduler_type

        # Create a header
        header = tk.Frame(self, bg=colors['button_bg'], height=60)
        header.pack(fill=tk.X, side=tk.TOP)

        back_button = tk.Button(
            header, text="← Back to Scheduler", command=lambda: self.navigate_to_scheduler(back_direction="right"),
            bg=colors['button_bg'], fg=colors['button_fg'],
            bd=0, font=("Arial", 12, "bold")
        )
        back_button.pack(side=tk.LEFT, padx=15, pady=10)

        home_button = tk.Button(
            header, text="Home", command=navigate_home,
            bg=colors['button_bg'], fg=colors['button_fg'],
            bd=0, font=("Arial", 12, "bold")
        )
        home_button.pack(side=tk.RIGHT, padx=15, pady=10)

        title_label = tk.Label(
            header, text=f"{scheduler_type} Scheduler Results", font=("Arial", 16, "bold"),
            bg=colors['button_bg'], fg=colors['button_fg']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Main container
        main_frame = tk.Frame(self, bg=colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Gantt Chart Section
        gantt_frame = tk.LabelFrame(
            main_frame, text="Final Gantt Chart", font=("Arial", 14, "bold"),
            bg=colors['background'], fg=colors['text'],
            padx=10, pady=10
        )
        gantt_frame.pack(fill=tk.X, pady=(0, 20))

        # Create a container for the Gantt chart with scrollbars
        gantt_container = tk.Frame(gantt_frame, bg=colors['background'])
        gantt_container.pack(fill=tk.X, expand=False)
        
        # Add horizontal scrollbar for gantt chart
        gantt_h_scroll = tk.Scrollbar(gantt_container, orient="horizontal")
        gantt_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add vertical scrollbar for gantt chart
        gantt_v_scroll = tk.Scrollbar(gantt_container, orient="vertical")
        gantt_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the canvas with fixed height of 250px
        self.gantt_canvas = tk.Canvas(
            gantt_container, bg="white", 
            height=250, 
            highlightthickness=1, 
            highlightbackground=colors['button_bg'],
            xscrollcommand=gantt_h_scroll.set,
            yscrollcommand=gantt_v_scroll.set
        )
        self.gantt_canvas.pack(fill=tk.X, expand=False)
        
        # Configure the scrollbars to work with the canvas
        gantt_h_scroll.config(command=self.gantt_canvas.xview)
        gantt_v_scroll.config(command=self.gantt_canvas.yview)

        # Statistics Section
        stats_frame = tk.LabelFrame(
            main_frame, text="Performance Metrics", font=("Arial", 14, "bold"),
            bg=colors['background'], fg=colors['text'],
            padx=10, pady=10
        )
        stats_frame.pack(fill=tk.X)

        # Create a flexible layout to place table on left and stats on right
        metrics_container = tk.Frame(stats_frame, bg=colors['background'])
        metrics_container.pack(fill=tk.X, padx=10, pady=10)

        # Left side - Create a scrollable container for the table
        table_container = tk.Frame(metrics_container, bg=colors['background'])
        table_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Add scrollbar for the table
        table_scroll = tk.Scrollbar(table_container)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a canvas to hold the table with fixed height
        table_canvas = tk.Canvas(
            table_container, 
            bg=colors['background'],
            height=200,  # Fixed height
            width=900,   # Fixed width appropriate for the table
            yscrollcommand=table_scroll.set,
            highlightthickness=0
        )
        table_canvas.pack(side=tk.LEFT)
        table_scroll.config(command=table_canvas.yview)
        
        # Create a frame inside the canvas for the actual table
        table_frame = tk.Frame(table_canvas, bg=colors['background'])
        table_window = table_canvas.create_window((0, 0), window=table_frame, anchor="nw")
        
        # Ensure the scroll region updates when the table size changes
        def configure_table_scroll_region(event):
            table_canvas.configure(scrollregion=table_canvas.bbox("all"))
        
        table_frame.bind('<Configure>', configure_table_scroll_region)

        # Table headers
        headers = ["Process", "Arrival Time", "Burst Time", "Completion Time",
                   "Turnaround Time", "Waiting Time"]

        for col, header in enumerate(headers):
            tk.Label(
                table_frame, text=header, font=("Arial", 12, "bold"),
                bg=colors['button_bg'], fg=colors['button_fg'],
                padx=10, pady=5, relief=tk.RIDGE, width=12
            ).grid(row=0, column=col, sticky="nsew")

        # Calculate and populate process statistics
        self.process_stats = self.calculate_process_stats()

        for row, (process_name, stats) in enumerate(self.process_stats.items(), start=1):
            tk.Label(
                table_frame, text=process_name, font=("Arial", 11),
                bg=colors['background'], fg=colors['text'],
                padx=10, pady=5, relief=tk.RIDGE
            ).grid(row=row, column=0, sticky="nsew")

            for col, metric in enumerate([
                stats['arrival_time'],
                stats['burst_time'],
                stats['completion_time'],
                stats['turnaround_time'],
                stats['waiting_time']
            ], start=1):
                tk.Label(
                    table_frame, text=str(metric), font=("Arial", 11),
                    bg=colors['background'], fg=colors['text'],
                    padx=10, pady=5, relief=tk.RIDGE
                ).grid(row=row, column=col, sticky="nsew")

        # Right side - Summary statistics
        avg_stats_frame = tk.Frame(metrics_container, bg=colors['background'])
        avg_stats_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Calculate averages
        avg_turnaround, avg_waiting = self.calculate_averages()

        # Average Turnaround Time Card
        avg_tat_frame = tk.Frame(avg_stats_frame, bg=colors['button_bg'],
                                 padx=30, pady=15, relief=tk.RAISED, bd=1)
        avg_tat_frame.pack(side=tk.TOP, pady=(0, 15), fill=tk.X)

        tk.Label(
            avg_tat_frame, text="Average Turnaround Time", font=("Arial", 12, "bold"),
            bg=colors['button_bg'], fg="white"
        ).pack()

        # Make sure the value appears with explicit contrasting color
        avg_tat_value = tk.Label(
            avg_tat_frame, text=f"{avg_turnaround:.2f} seconds", font=("Arial", 16, "bold"),
            bg=colors['button_bg'], fg="white"
        )
        avg_tat_value.pack(pady=5)

        # Average Waiting Time Card
        avg_wt_frame = tk.Frame(avg_stats_frame, bg=colors['button_bg'],
                                padx=20, pady=15, relief=tk.RAISED, bd=1)
        avg_wt_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(
            avg_wt_frame, text="Average Waiting Time", font=("Arial", 12, "bold"),
            bg=colors['button_bg'], fg="white"
        ).pack()

        # Make sure the value appears with explicit contrasting color
        avg_wt_value = tk.Label(
            avg_wt_frame, text=f"{avg_waiting:.2f} seconds", font=("Arial", 16, "bold"),
            bg=colors['button_bg'], fg="white"
        )
        avg_wt_value.pack(pady=5)

        # Draw the Gantt chart
        self.draw_gantt_chart()

    def calculate_process_stats(self):
        """Calculate statistics for each process."""
        stats = {}

        # First, get the process details (name, arrival, burst)
        for process in self.completed_processes:
            name = process[0]
            burst_time = process[1]
            arrival_time = process[2]

            stats[name] = {
                'name': name,
                'arrival_time': arrival_time,
                'burst_time': burst_time,
                'completion_time': 0,  # Will be calculated from execution history
                'turnaround_time': 0,  # Will be calculated: completion - arrival
                'waiting_time': 0  # Will be calculated: turnaround - burst
            }

        # Calculate completion times from execution history
        if self.process_execution_history:
            # Group by process name
            process_executions = {}
            for name, start, end, status in self.process_execution_history:
                if status == "running":
                    process_executions.setdefault(name, []).append((start, end))

            # Find last execution for each process (completion time)
            for name, executions in process_executions.items():
                if name in stats:
                    # Use the end time of the last execution segment
                    stats[name]['completion_time'] = max(end for _, end in executions)
                    # Calculate turnaround and waiting times
                    stats[name]['turnaround_time'] = stats[name]['completion_time'] - stats[name]['arrival_time']
                    stats[name]['waiting_time'] = stats[name]['turnaround_time'] - stats[name]['burst_time']

        return stats

    def calculate_averages(self):
        """Calculate average turnaround and waiting times."""
        if not self.process_stats:
            return 0, 0

        total_turnaround = sum(stats['turnaround_time'] for stats in self.process_stats.values())
        total_waiting = sum(stats['waiting_time'] for stats in self.process_stats.values())
        count = len(self.process_stats)

        return total_turnaround / count, total_waiting / count

    def draw_gantt_chart(self):
        """Draw the Gantt chart on the canvas."""
        self.gantt_canvas.delete("all")
        canvas_width = self.width - 100
        canvas_height = 250
        margin = 70

        # Determine the maximum time from execution history
        if not self.process_execution_history:
            self.gantt_canvas.create_text(
                canvas_width // 2, canvas_height // 2,
                text="No execution data available", font=("Arial", 14)
            )
            return

        # Count the unique processes and determine required height
        unique_processes = sorted(set(name for name, _, _, _ in self.process_execution_history))
        process_count = len(unique_processes)
        
        # Calculate needed height for all processes with spacing
        bar_height = 25
        bar_spacing = 10
        y_offset = 30  # Space at top
        required_height = y_offset + (process_count * (bar_height + bar_spacing)) + 50  # +50 for time axis at bottom
        
        # Set the scroll region to accommodate all processes vertically
        self.gantt_canvas.configure(scrollregion=(0, 0, canvas_width, max(canvas_height, required_height)))

        total_time = max(end for _, _, end, _ in self.process_execution_history)
        time_scale = (canvas_width - margin - 20) / max(1, total_time)
        
        # If the timeline is long, make the scroll region wider to ensure all time points are visible
        if total_time > 20:  # If we have many time points
            extended_width = margin + (total_time * max(time_scale, 20)) + 20
            self.gantt_canvas.configure(scrollregion=(0, 0, max(canvas_width, extended_width), max(canvas_height, required_height)))

        # Time axis
        self.gantt_canvas.create_line(margin, max(canvas_height, required_height) - 30, canvas_width - 10, max(canvas_height, required_height) - 30, width=2)
        self.gantt_canvas.create_text(
            canvas_width // 2, max(canvas_height, required_height) - 10,
            text="Time (seconds)", font=("Arial", 10, "bold")
        )

        # Time labels
        tick_interval = max(1, math.ceil(total_time / 10))  # Adjust for readability
        for t in range(0, total_time + 1, tick_interval):
            x = margin + t * time_scale
            self.gantt_canvas.create_line(x, max(canvas_height, required_height) - 30, x, max(canvas_height, required_height) - 25, width=2)
            self.gantt_canvas.create_text(x, max(canvas_height, required_height) - 15, text=str(t), font=("Arial", 8))

        self.gantt_canvas.create_text(margin // 2, 10, text="Process", font=("Arial", 10, "bold"))

        # Assign colors for processes
        process_colors = [
            "#4CAF50", "#2196F3", "#FFC107", "#9C27B0", "#F44336",
            "#009688", "#795548", "#607D8B", "#E91E63", "#673AB7",
            "#3F51B5", "#FF9800", "#CDDC39", "#8BC34A", "#00BCD4"  # Added more colors
        ]
        process_color_map = {
            proc: process_colors[i % len(process_colors)]
            for i, proc in enumerate(unique_processes)
        }

        # Group segments by process
        process_timelines = {}
        for name, start, end, status in self.process_execution_history:
            if status == "running":  # Only show running segments
                process_timelines.setdefault(name, []).append((start, end))

        # Draw process execution bars
        y_pos = y_offset
        for i, name in enumerate(unique_processes):
            color = process_color_map.get(name, "#CCCCCC")
            y = y_pos + i * (bar_height + bar_spacing)

            # Process name label
            self.gantt_canvas.create_text(
                margin - 5, y + bar_height / 2,
                text=name, anchor="e", font=("Arial", 10)
            )

            # Draw execution segments
            timeline = process_timelines.get(name, [])
            for start, end in timeline:
                x1 = margin + start * time_scale
                x2 = margin + end * time_scale

                self.gantt_canvas.create_rectangle(
                    x1, y, x2, y + bar_height, fill=color, outline="black"
                )

                # Show duration in the segment if width permits
                if (x2 - x1) > 30:
                    duration = end - start
                    self.gantt_canvas.create_text(
                        (x1 + x2) / 2, y + bar_height / 2,
                        text=f"{duration}s", font=("Arial", 9), fill="black"
                    )
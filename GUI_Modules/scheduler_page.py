
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

class SchedulerPage(tk.Frame):
    def __init__(self, parent, colors, width, height, navigate_home, navigate_live_scheduler):
        super().__init__(parent, bg=colors['background'])
        self.colors = colors
        self.navigate_home = navigate_home
        self.navigate_live_scheduler = navigate_live_scheduler

        self.entries = {}
        self.priority_var = {}
        self.process_list = {
            "FCFS": [],
            "SJF": [],
            "Priority": [],
            "Round Robin": []
        }
        self.process_widgets = {
            "FCFS": [],
            "SJF": [],
            "Priority": [],
            "Round Robin": []
        }

        self.live_scheduler_enabled = tk.BooleanVar(value=False)
        self.rr_quantum = tk.StringVar(value="2")

        self.frame = ctk.CTkScrollableFrame(master=self, width=width, height=height,
                                            corner_radius=15, fg_color=colors['background'])
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        title_label = ctk.CTkLabel(self.frame, text="CPU Scheduling Simulator",
                                   font=("Arial", 20, "bold"), text_color=colors['text'])
        title_label.pack(pady=10)

        self.tabview = ctk.CTkTabview(self.frame, width=500, height=50,
                                      fg_color="#0A0A0A",
                                      segmented_button_fg_color="#CDA457",
                                      segmented_button_selected_color="#8A7439",
                                      segmented_button_unselected_color="#0A0A0A")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        for tab_name in ["FCFS", "SJF", "Priority", "Round Robin"]:
            self.tabview.add(tab_name)

        self.create_fcfs_tab()
        self.create_sjf_tab()
        self.create_priority_tab()
        self.create_round_robin_tab()

        # Live Scheduler Checkbox
        ctk.CTkCheckBox(
            self.frame,
            text="Live Scheduler",
            variable=self.live_scheduler_enabled,
            text_color=self.colors['text']
        ).pack(pady=5)

        button_frame1 = ctk.CTkFrame(self.frame, fg_color=colors['background'])
        button_frame1.pack(pady=5)

        ctk.CTkButton(button_frame1, text="Show Scheduler", fg_color=colors['button_bg'],
                      hover_color=colors['toggle_bg'], text_color=colors['button_fg'],
                      font=("Arial", 14, "bold"), corner_radius=10,
                      command=lambda: self.on_run_live_scheduler(self.process_list)).pack(side="left", pady=5, padx=10)

        ctk.CTkButton(button_frame1, text="Add Process", fg_color=colors['button_bg'],
                      hover_color=colors['toggle_bg'], text_color=colors['button_fg'],
                      font=("Arial", 14, "bold"), corner_radius=10,
                      command=self.add_process_by_selected_tab).pack(side="left", pady=10, padx=10)

        ctk.CTkButton(button_frame1, text="Clear All Process", fg_color=colors['sign_out_bg'],
                      hover_color=colors['toggle_bg'], text_color=colors['sign_out_fg'],
                      font=("Arial", 14, "bold"), corner_radius=10,
                      command=self.clear_process_by_selected_tab).pack(side="left", pady=10, padx=10)

        ctk.CTkLabel(self.frame, text="If you enter more than one process type, the scheduler will only run the last type entered.",
                     font=("Arial", 10, "bold"), text_color=self.colors['text']).pack(pady=10)

        self.process_display = ctk.CTkFrame(self.frame, fg_color=colors['background'])
        self.process_display.pack(pady=10, fill="both", expand=True)

    def clear_process_by_selected_tab(self):
        tab = self.tabview.get()
        self.process_list[tab].clear()
        for widget in self.process_widgets[tab]:
            widget.destroy()
        self.process_widgets[tab].clear()

    def add_process_by_selected_tab(self):
        selected_tab = self.tabview.get()
        if any(entry.get().strip() == "" for entry in self.entries[selected_tab].values()):
            messagebox.showerror("Error", "Please fill all fields.")
            return

        for field, entry in self.entries[selected_tab].items():
            value = entry.get().strip()
            if field != "Process Name" and not value.isdigit():
                return

        new_process_name = self.entries[selected_tab]["Process Name"].get().strip()
        for process in self.process_list[selected_tab]:
            if process["Process Name"] == new_process_name:
                messagebox.showerror("Error", f"A process named '{new_process_name}' already exists.")
                return

        new_burst = self.entries[selected_tab]["Burst Time"].get().strip()
        if int(new_burst) == 0:
            messagebox.showerror("Error", "Burst Time can't be zero.")
            return

        self.collect_data(selected_tab)

    def collect_data(self, tab):
        data = {
            "Type": tab,
            "Process Name": self.entries[tab]["Process Name"].get(),
            "Arrival Time": self.entries[tab]["Arrival Time"].get(),
            "Burst Time": self.entries[tab]["Burst Time"].get()
        }

        if tab == "Priority":
            data["Priority"] = self.entries[tab]["Priority"].get()
        if tab == "Round Robin":
            data["Quantum"] = self.rr_quantum.get()
        if tab in ["SJF", "Priority"]:
            data["Scheduling Type"] = self.priority_var[tab].get()

        self.process_list[tab].append(data)
        self.display_process(tab, data)

    def display_process(self, tab, data):
        process_text = ', '.join([f"{k}: {v}" for k, v in data.items()])
        container = ctk.CTkFrame(self.process_display, fg_color="#0A0A0A",
                                 border_color="#CDA457", border_width=1, corner_radius=8)
        container.pack(pady=5, fill="x", padx=20)

        label = ctk.CTkLabel(container, text=process_text, anchor="w", justify="left",
                             text_color=self.colors['text'])
        label.pack(side="left", padx=5, fill="x", expand=True)

        remove_btn = ctk.CTkButton(container, text="Remove", fg_color=self.colors['sign_out_bg'],
                                   text_color=self.colors['sign_out_fg'], width=80,
                                   command=lambda: self.remove_process(tab, data, container))
        remove_btn.pack(side="right", padx=5)

        self.process_widgets[tab].append(container)

    def remove_process(self, tab, data, widget):
        if data in self.process_list[tab]:
            self.process_list[tab].remove(data)
        widget.destroy()
        if widget in self.process_widgets[tab]:
            self.process_widgets[tab].remove(widget)

    def validate_integer_input(self, event, entry_widget):
        value = entry_widget.get()
        if value and not value.isdigit():
            messagebox.showerror("Error", "Input must be an integer.")
            entry_widget.delete(0, tk.END)

    def validate_quantum(self, event, entry_widget):
        value = entry_widget.get()
        if not value or not value.isdigit() or int(value) <= 0:
            messagebox.showerror("Error", "Time quantum must be a positive integer.")
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, "2")

    def get_formatted_processes(self):
        formatted = []
        tab = self.tabview.get()
        for process in self.process_list[tab]:
            name = process["Process Name"]
            arrival = int(process["Arrival Time"])
            burst = int(process["Burst Time"])

            if tab == "FCFS":
                formatted.append([name, burst, arrival])
            elif tab == "SJF":
                preemptive = process.get("Scheduling Type", "Non-Preemptive") == "Preemptive"
                formatted.append([name, burst, arrival, preemptive])
            elif tab == "Priority":
                priority = int(process["Priority"])
                preemptive = process.get("Scheduling Type", "Non-Preemptive") == "Preemptive"
                formatted.append([name, burst, arrival, priority, preemptive])
            elif tab == "Round Robin":
                quantum = int(process["Quantum"])
                formatted.append([name, burst, arrival, quantum])
        return formatted

    def on_run_live_scheduler(self, process_list):
        if all(len(v) == 0 for v in self.process_list.values()):
            messagebox.showerror("Error", "Please enter processes.")
            return

        if self.navigate_live_scheduler:
            current_tab = self.tabview.get()
            formatted_processes = self.get_formatted_processes()
            flag = self.live_scheduler_enabled.get()
            self.navigate_live_scheduler(formatted_processes, current_tab, flag)

    def on_back_button_click(self):
        if self.navigate_home:
            self.navigate_home()

    def create_fcfs_tab(self):
        self.entries["FCFS"] = {}
        for field in ["Process Name", "Arrival Time", "Burst Time"]:
            entry = ctk.CTkEntry(self.tabview.tab("FCFS"), width=400, height=40,
                                 corner_radius=10, placeholder_text=field,
                                 fg_color=self.colors['background'],
                                 text_color=self.colors['text'],
                                 placeholder_text_color=self.colors['text_secondary'])
            entry.pack(pady=5)
            self.entries["FCFS"][field] = entry
            if field != "Process Name":
                entry.bind("<FocusOut>", lambda e, ent=entry: self.validate_integer_input(e, ent))

    def create_sjf_tab(self):
        self.entries["SJF"] = {}
        for field in ["Process Name", "Arrival Time", "Burst Time"]:
            entry = ctk.CTkEntry(self.tabview.tab("SJF"), width=400, height=40,
                                 corner_radius=10, placeholder_text=field,
                                 fg_color=self.colors['background'],
                                 text_color=self.colors['text'],
                                 placeholder_text_color=self.colors['text_secondary'])
            entry.pack(pady=5)
            self.entries["SJF"][field] = entry
            if field != "Process Name":
                entry.bind("<FocusOut>", lambda e, ent=entry: self.validate_integer_input(e, ent))

        self.priority_var["SJF"] = ctk.StringVar(value="Non-Preemptive")
        radio_frame = ctk.CTkFrame(self.tabview.tab("SJF"), fg_color=self.colors['background'])
        radio_frame.pack(pady=5)
        ctk.CTkRadioButton(radio_frame, text="Non-Preemptive", variable=self.priority_var["SJF"],
                           value="Non-Preemptive", text_color=self.colors['text']).pack(side="left", padx=5)
        ctk.CTkRadioButton(radio_frame, text="Preemptive", variable=self.priority_var["SJF"],
                           value="Preemptive", text_color=self.colors['text']).pack(side="left", padx=20)

    def create_priority_tab(self):
        self.entries["Priority"] = {}
        for field in ["Process Name", "Arrival Time", "Burst Time", "Priority"]:
            entry = ctk.CTkEntry(self.tabview.tab("Priority"), width=400, height=40,
                                 corner_radius=10, placeholder_text=field,
                                 fg_color=self.colors['background'],
                                 text_color=self.colors['text'],
                                 placeholder_text_color=self.colors['text_secondary'])
            entry.pack(pady=5)
            self.entries["Priority"][field] = entry
            if field != "Process Name":
                entry.bind("<FocusOut>", lambda e, ent=entry: self.validate_integer_input(e, ent))

        self.priority_var["Priority"] = ctk.StringVar(value="Non-Preemptive")
        radio_frame = ctk.CTkFrame(self.tabview.tab("Priority"), fg_color=self.colors['background'])
        radio_frame.pack(pady=5)
        ctk.CTkRadioButton(radio_frame, text="Non-Preemptive", variable=self.priority_var["Priority"],
                           value="Non-Preemptive", text_color=self.colors['text']).pack(side="left", padx=5)
        ctk.CTkRadioButton(radio_frame, text="Preemptive", variable=self.priority_var["Priority"],
                           value="Preemptive", text_color=self.colors['text']).pack(side="left", padx=20)

    def create_round_robin_tab(self):
        self.entries["Round Robin"] = {}
        quantum_settings_frame = ctk.CTkFrame(self.tabview.tab("Round Robin"), fg_color=self.colors['background'])
        quantum_settings_frame.pack(pady=(10, 20), fill="x")

        ctk.CTkLabel(quantum_settings_frame, text="Time Quantum (for all processes):",
                     text_color=self.colors['text']).pack(side="left", padx=(10, 5))

        quantum_entry = ctk.CTkEntry(quantum_settings_frame, width=80,
                                     textvariable=self.rr_quantum,
                                     fg_color=self.colors['background'],
                                     text_color=self.colors['text'])
        quantum_entry.pack(side="left", padx=5)
        quantum_entry.bind("<FocusOut>", lambda e: self.validate_quantum(e, quantum_entry))

        separator_label = ctk.CTkLabel(self.tabview.tab("Round Robin"),
                                       text="Process Details",
                                       font=("Arial", 12, "bold"),
                                       text_color=self.colors['text'])
        separator_label.pack(pady=(0, 10))

        for field in ["Process Name", "Arrival Time", "Burst Time"]:
            entry = ctk.CTkEntry(self.tabview.tab("Round Robin"), width=400, height=40,
                                 corner_radius=10, placeholder_text=field,
                                 fg_color=self.colors['background'],
                                 text_color=self.colors['text'],
                                 placeholder_text_color=self.colors['text_secondary'])
            entry.pack(pady=5)
            self.entries["Round Robin"][field] = entry
            if field != "Process Name":
                entry.bind("<FocusOut>", lambda e, ent=entry: self.validate_integer_input(e, ent))

import tkinter as tk
import customtkinter


class HomeScreen(tk.Frame):
    def __init__(self, parent, colors, show_scheduler_page, toggle_theme):
        super().__init__(parent, bg=colors['background'])
        
        self.colors = colors
        self.show_scheduler_page = show_scheduler_page 
        self.toggle_theme = toggle_theme 
        self.create_home_screen()
        
    def create_home_screen(self):
        # Set title
        self.master.title("Welcome Page")
        
        # Create header frame
        header = tk.Frame(self, bg=self.colors['background'], height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        
        # Toggle theme button
        toggle_button = tk.Button(
            header,
            text="🌗", 
            bd=0, bg=self.colors['background'],
            font=("Arial", 12, "bold"), 
            command=self.toggle_theme  
        )
        toggle_button.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Main title
        main_title_label = customtkinter.CTkLabel(
            master=self, 
            text="CPU Scheduling Simulator", 
            font=("Arial", 30, "bold"),
            text_color="gray"
        )
        main_title_label.pack(pady=(100, 10))

        # Subtitle
        subtitle_label = customtkinter.CTkLabel(
            master=self, 
            text="Simulate & Analyze CPU Scheduling Algorithms", 
            font=("Arial", 14),
            text_color="gray"
        )
        subtitle_label.pack(pady=(5, 30))

        # Start button (Switch to Scheduler Page)
        start_button = customtkinter.CTkButton(
            master=self, 
            text="Start Simulation", 
            fg_color="#3498db", 
            hover_color="#2980b9", 
            font=("Arial", 20, "bold"), 
            corner_radius=12, 
            width=250, 
            height=60, 
            command=self.show_scheduler_page  # Ensure this function is defined
        )
        start_button.pack(anchor="center", pady=(10, 20))

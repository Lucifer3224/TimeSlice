import tkinter as tk
import customtkinter

class HomeScreen(tk.Frame):
    def __init__(self, parent, colors, show_scheduler_page, toggle_theme):
        super().__init__(parent, bg=colors['background'])
        self.colors = colors
        self.show_scheduler_page = show_scheduler_page  # Function to switch to the scheduler page
        self.toggle_theme = toggle_theme  # Function to toggle theme
        self.create_home_screen()

    def create_home_screen(self):
        # Set title
        self.master.title("TimeSlice")

        # Main Title
        main_title_label = customtkinter.CTkLabel(
            master=self,
            text="CPU Scheduling Simulator",
            font=("Georgia", 30, "bold"),  # More elegant font
            text_color="#CDA457"  # Gold text
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

        # Start Button (Switch to Scheduler Page)
        start_button = customtkinter.CTkButton(
            master=self,
            text="Start Simulation",
            fg_color="#CDA457",  # Gold background
            hover_color="#8A7439",  # Darker gold on hover
            text_color="#000000",  # Black text
            font=("Arial", 20, "bold"),
            corner_radius=12,
            width=250,
            height=60,
            command=self.show_scheduler_page
        )
        start_button.pack(anchor="center", pady=(10, 20))
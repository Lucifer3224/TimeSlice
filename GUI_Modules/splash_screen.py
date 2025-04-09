import tkinter as tk
from PIL import Image, ImageTk
import time

from GUI_Modules.output import OutputPage
from GUI_Modules.scheduler_page import SchedulerPage
from GUI_Modules.home_screen import HomeScreen
from GUI_Modules.live_scheduler_page import LiveSchedulerPage

class SplashScreenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TimeSlice")
        self.root.overrideredirect(False)  # Allow standard window decoration
        self.process_list = None
        # Initialize theme - using logo colors
        self.dark_mode = False
        self.logo_bg_color = "#F5EDD7"  # Cream/beige from logo
        self.logo_blue = "#3D8BAE"  # Blue from the clock
        self.logo_dark = "#1A1A1A"  # Dark color for text
        self.colors = self.get_theme_colors()

        # Get screen dimensions for centering
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set initial window size
        self.window_width = 800
        self.window_height = 600

        # Center the window
        x_position = (screen_width - self.window_width) // 2
        y_position = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x_position}+{y_position}")

        # Configure window to expand properly
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Initialize screens
        self.current_screen = 0
        self.screens = []
        self.page_screens = {}  # Dictionary to track actual application pages
        self.home_screen = None  # Reference to home screen

        # Create the logo screen
        self.create_logo_screen()

        # Bind events
        self.root.bind("<Key>", self.next_screen)
        self.root.bind("<Button-1>", self.next_screen)
        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            old_width = self.window_width
            old_height = self.window_height

            # Ignore minimize events
            if event.width <= 1 or event.height <= 1:
                return

            self.window_width = event.width
            self.window_height = event.height

            # Only resize screens, but don't trigger the transition logic
            if abs(old_width - self.window_width) > 10 or abs(old_height - self.window_height) > 10:
                for i, screen in enumerate(self.screens):
                    screen.place(x=0, y=0, width=self.window_width, height=self.window_height)

                    # Ensure the current screen remains in focus
                    if i == self.current_screen:
                        screen.lift()

    def get_theme_colors(self):
        """Get color scheme based on current theme"""
        if self.dark_mode:
            return {
                'background': '#121212',
                'text': '#FFFFFF',
                'text_secondary': '#BBBBBB',
                'button_bg': self.logo_blue,
                'button_fg': '#FFFFFF',
                'sign_out_bg': '#CF6679',
                'sign_out_fg': '#FFFFFF',
                'toggle_bg': '#03DAC6',
                'toggle_fg': '#000000'
            }
        else:
            return {
                'background': self.logo_bg_color,
                'text': self.logo_dark,
                'text_secondary': '#555555',
                'button_bg': self.logo_blue,
                'button_fg': '#FFFFFF',
                'sign_out_bg': '#B00020',
                'sign_out_fg': '#FFFFFF',
                'toggle_bg': '#00BCD4',
                'toggle_fg': '#000000'
            }

    def show_home_screen(self):
        """Show the Home Screen"""
        if self.home_screen is None:
            self.home_screen = HomeScreen(self.root, self.colors, self.show_scheduler_page, self.toggle_theme)
            self.screens.append(self.home_screen)
            self.page_screens['home'] = self.home_screen

            # Use slide transition from second splash to home
            self.slide_transition(self.screens[self.current_screen], self.home_screen, direction="left")
            self.current_screen = len(self.screens) - 1
        else:
            # If returning to home screen
            current_frame = self.screens[self.current_screen]
            home_index = self.screens.index(self.home_screen)

            # Use right direction for back navigation
            self.slide_transition(current_frame, self.home_screen, direction="right")
            self.current_screen = home_index

    def show_scheduler_page(self):
        """Show the Scheduler Page"""
        # Check if scheduler already exists
        scheduler_page = None
        if 'scheduler' in self.page_screens:
            scheduler_page = self.page_screens['scheduler']
        else:
            # Create new scheduler page and store reference.
            # Note: Pass self.show_home_screen as navigate_home and
            # self.show_live_scheduler_page as navigate_live_scheduler.
            scheduler_page = SchedulerPage(self.root, self.colors, self.window_width, self.window_height,
                                           self.show_home_screen, self.show_live_scheduler_page)
            self.screens.append(scheduler_page)
            self.page_screens['scheduler'] = scheduler_page

        # Use slide transition for page navigation
        self.slide_transition(self.screens[self.current_screen], scheduler_page, direction="left")
        self.current_screen = self.screens.index(scheduler_page)

    def show_live_scheduler_page(self, process_list, scheduler_type="FCFS"):
        """Show the Live Scheduler Page"""
        live_scheduler_page = None

        if 'live_scheduler' in self.page_screens:
            # Replace existing page to ensure we get fresh parameters
            live_scheduler_page = LiveSchedulerPage(
                self.root, self.colors, self.window_width, self.window_height,
                self.show_home_screen, process_list, scheduler_type,
                navigate_to_output=self.show_output_page  # Add this parameter
            )
            self.screens[self.screens.index(self.page_screens['live_scheduler'])] = live_scheduler_page
            self.page_screens['live_scheduler'] = live_scheduler_page
        else:
            live_scheduler_page = LiveSchedulerPage(
                self.root, self.colors, self.window_width, self.window_height,
                self.show_home_screen, process_list, scheduler_type,
                navigate_to_output=self.show_output_page  # Add this parameter
            )
            self.screens.append(live_scheduler_page)
            self.page_screens['live_scheduler'] = live_scheduler_page

        self.slide_transition(self.screens[self.current_screen], live_scheduler_page, direction="left")
        self.current_screen = self.screens.index(live_scheduler_page)

    def show_output_page(self, completed_processes=None, process_execution_history=None):
        """Show the Output Page with scheduling results"""
        output_page = None

        # Get the scheduler type from the current live scheduler page
        scheduler_type = "FCFS"  # Default
        if 'live_scheduler' in self.page_screens:
            scheduler_type = self.page_screens['live_scheduler'].scheduler_type

        if 'output_page' in self.page_screens:
            # Replace existing page
            output_page = OutputPage(
                self.root, self.colors, self.window_width, self.window_height,
                self.show_home_screen,
                lambda: self.show_live_scheduler_page(self.process_list, scheduler_type),
                completed_processes, process_execution_history, scheduler_type
            )
            self.screens[self.screens.index(self.page_screens['output_page'])] = output_page
            self.page_screens['output_page'] = output_page
        else:
            output_page = OutputPage(
                self.root, self.colors, self.window_width, self.window_height,
                self.show_home_screen,
                lambda: self.show_live_scheduler_page(self.process_list, scheduler_type),
                completed_processes, process_execution_history, scheduler_type
            )
            self.screens.append(output_page)
            self.page_screens['output_page'] = output_page

        self.slide_transition(self.screens[self.current_screen], output_page, direction="left")
        self.current_screen = self.screens.index(output_page)


    def toggle_theme(self):
        """Switch between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.colors = self.get_theme_colors()
        self.update_screen_colors()

    def update_screen_colors(self):
        """Update colors of all existing screens"""
        for screen in self.screens:
            screen.configure(bg=self.colors['background'])
            if hasattr(screen, 'update_colors'):
                screen.update_colors(self.colors)
            else:
                self.update_widget_colors(screen)

    def update_widget_colors(self, parent):
        """Recursively update colors of all widgets"""
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=self.colors['background'], fg=self.colors['text'])
                if widget.cget('text').startswith("Activity item"):
                    widget.configure(fg=self.colors['text_secondary'])
            elif isinstance(widget, tk.Button):
                if widget.cget('text') == "Toggle Theme":
                    widget.configure(bg=self.colors['toggle_bg'], fg=self.colors['toggle_fg'])
                elif widget.cget('text') == "Sign Out":
                    widget.configure(bg=self.colors['sign_out_bg'], fg=self.colors['sign_out_fg'])
                else:
                    widget.configure(bg=self.colors['button_bg'], fg=self.colors['button_fg'])
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=self.colors['background'])
                self.update_widget_colors(widget)

    def create_logo_screen(self):
        """Create the first screen with company logo"""
        logo_frame = tk.Frame(self.root, bg=self.colors['background'])
        logo_frame.place(x=0, y=0, width=self.window_width, height=self.window_height)
        logo_container = tk.Frame(logo_frame, bg=self.colors['background'])
        logo_container.place(relx=0.5, rely=0.5, anchor='center')
        try:
            logo_img = Image.open('ChatGPT Image Mar 30, 2025, 08_27_34 AM.png')
            width, height = logo_img.size
            center_x, center_y = width // 2, height // 2
            crop_radius = min(width, height) // 2.5
            logo_img = logo_img.crop(
                (center_x - crop_radius, center_y - crop_radius - 40, center_x + crop_radius, center_y + crop_radius))
            logo_size = 300
            logo_img = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(logo_container, image=logo_photo, bg=self.colors['background'])
            logo_label.image = logo_photo
            logo_label.pack()
            company_name = tk.Label(logo_container, text="TimeSlice", font=("Arial", 36, "bold"),
                                    bg=self.colors['background'], fg=self.colors['text'])
            company_name.pack(pady=20)
        except Exception as e:
            print(f"Error loading logo: {e}")
            logo_label = tk.Label(logo_container, text="TIMESLICE", font=("Arial", 48, "bold"),
                                  bg=self.colors['background'], fg=self.colors['text'])
            logo_label.pack()
        instruction = tk.Label(logo_frame, text="Click anywhere or press any key to continue", font=("Arial", 12),
                               bg=self.colors['background'], fg=self.colors['text_secondary'])
        instruction.place(relx=0.5, rely=0.9, anchor='center')
        self.screens.append(logo_frame)

    def create_app_name_screen(self):
        """Create the second screen with app name"""
        name_frame = tk.Frame(self.root, bg=self.colors['background'])
        name_frame.place(x=0, y=0, width=self.window_width, height=self.window_height)
        name_frame.lower()
        app_name = tk.Label(name_frame, text="TIMESLICE", font=("Arial", 64, "bold"), bg=self.colors['background'],
                            fg=self.colors['text'])
        app_name.place(relx=0.5, rely=0.5, anchor='center')
        tagline = tk.Label(name_frame, text="Track, Analyze, Optimize Your Time", font=("Arial", 18),
                           bg=self.colors['background'], fg=self.colors['text_secondary'])
        tagline.place(relx=0.5, rely=0.6, anchor='center')
        instruction = tk.Label(name_frame, text="Click anywhere or press any key to continue", font=("Arial", 12),
                               bg=self.colors['background'], fg=self.colors['text_secondary'])
        instruction.place(relx=0.5, rely=0.9, anchor='center')
        self.screens.append(name_frame)

    def fade_transition(self, current_frame, next_frame):
        """Animate fade-out fade-in transition between screens"""
        next_frame.place(x=0, y=0, width=self.window_width, height=self.window_height)
        next_frame.lift()
        overlay = tk.Frame(next_frame, bg=self.colors['background'])
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        steps = 15
        for i in range(steps):
            alpha = 1 - (i / steps)
            current_frame.update()
            time.sleep(0.03)
        for i in range(steps + 1):
            alpha = i / steps
            overlay.place_configure(relwidth=1 - alpha)
            next_frame.update()
            time.sleep(0.03)
        overlay.destroy()
        current_frame.place_forget()

    def slide_transition(self, current_frame, next_frame, direction="left"):
        """Animate slide transition between screens"""
        if direction == "left":
            next_frame.place(x=self.window_width, y=0, width=self.window_width, height=self.window_height)
        elif direction == "right":
            next_frame.place(x=-self.window_width, y=0, width=self.window_width, height=self.window_height)
        else:
            next_frame.place(x=0, y=0, width=self.window_width, height=self.window_height)
            current_frame.place_forget()
            return

        next_frame.lift()
        steps = 20
        step_size = self.window_width // steps
        for i in range(steps + 1):
            if direction == "left":
                current_x = -i * step_size
                next_x = self.window_width + current_x
            elif direction == "right":
                current_x = i * step_size
                next_x = -self.window_width + current_x
            current_frame.place(x=current_x, y=0, width=self.window_width, height=self.window_height)
            next_frame.place(x=next_x, y=0, width=self.window_width, height=self.window_height)
            self.root.update()
            time.sleep(0.01)
        current_frame.place_forget()
        next_frame.place(x=0, y=0, width=self.window_width, height=self.window_height)

    def next_screen(self, event=None):
        """Move to the next screen when user interacts"""
        if self.current_screen >= len(self.screens) - 1 and self.current_screen >= 2:
            return
        if hasattr(event, "x") and event.x > self.window_width - 100 and event.y < 30:
            return
        if self.current_screen == 0 and len(self.screens) == 1:
            self.create_app_name_screen()
            current_frame = self.screens[self.current_screen]
            next_frame = self.screens[self.current_screen + 1]
            self.fade_transition(current_frame, next_frame)
            self.current_screen += 1
        elif self.current_screen == 1 and len(self.screens) == 2:
            self.show_home_screen()
        if self.current_screen == 2:
            self.root.unbind("<Key>")
            self.root.unbind("<Button-1>")

if __name__ == "__main__":
    root = tk.Tk()
    app = SplashScreenApp(root)
    root.mainloop()

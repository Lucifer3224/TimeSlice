import tkinter as tk
from GUI_Modules.splash_screen import SplashScreenApp

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = SplashScreenApp(root)
    root.deiconify()
    root.mainloop()
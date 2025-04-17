# TimeSlice
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-green?style=flat&logo=python)](https://wiki.python.org/moin/TkInter)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)

A visual CPU scheduling simulator written in Python that demonstrates how various scheduling algorithms manage process execution. The simulator features:

- 🟢 FCFS (First-Come First-Served)
- 🟡 SJF (Shortest Job First) – Preemptive & Non-Preemptive
- 🔵 Priority Scheduling – Preemptive & Non-Preemptive
- 🔁 Round Robin Scheduling

Built using **Tkinter**, **CustomTkinter**, and **Pillow**, this project provides a modern desktop GUI experience for educational purposes.

---

## 🚀 Features

- 🔧 Real-time CPU process scheduling animation
- 📊 Gantt chart updates live as processes execute
- 🧮 Average Turnaround & Waiting Time calculation
- 🌙 Light/Dark theme support
- 🧩 Modular schedulers for easy extension
- 🖥️ Built-in splash screen & multi-page navigation

---

## 🖥️ Screenshots

> *(Insert your screenshots or Gantt chart previews here)*  
> You can drag/drop them in GitHub's README editor after upload.

---

TimeSlice/ 

<pre> ``` TimeSlice/
  ├── GUI_Modules/ 
  │   ├── splash_screen.py # App launcher and screen controller 
  │   ├── home_screen.py # Welcome screen
  │   ├── scheduler_page.py # Algorithm selection and input form
  │   ├── live_scheduler_page.py # Simulation core logic and UI 
  │   └── output.py # Final output: Gantt + stats 
  │ ├── Schedulers/ 
  │   ├── fcfs_scheduler.py 
  │   ├── sjf_scheduler.py
  │   ├── priority_scheduler.py 
  │   └── round_robin_scheduler.py 
  │   ├── assets/
  │   └── ChatGPT Logo.png # Optional splash image
  │   └── README.md # Project documentation ``` </pre>

### 🔧 Requirements

- Python 3.10 or higher  
- CustomTkinter  
- Pillow

### 📥 Install dependencies


# ⚙️ Algorithms Logic Overview

Each algorithm is implemented in its own class with the following structure:

- `update_queues(current_time)`:  
  Moves arrived processes from waiting to ready queue.

- `run(...)`:  
  Executes the selected process per the algorithm’s logic.

- `timeline`:  
  Holds execution history (for Gantt chart).

- `completed`:  
  Stores finished processes with their stats.

---

# 📈 Output Metrics

Metrics are automatically calculated for each process:
- **Turnaround Time (TAT)** = Completion Time − Arrival Time
- **Waiting Time (WT)** = Turnaround Time − Burst Time
- **Average TAT & WT** are calculated and displayed at the end.

---

# 🚧 Planned Features

- [ ] Scrollable Gantt chart for large inputs
- [ ] Export output data to `.csv`
- [ ] Add multi-core CPU support
- [ ] Drag-and-drop process modification

---

# 👨‍💻 Author

**Mohamed Hamed**  
Faculty of Engineering – Ain Shams University  
**Course:** Operating Systems  
**Semester:** Spring 2025

---

# 📄 License

This project is licensed under the [MIT License](LICENSE).  
Free to use, modify, and contribute for academic or educational purposes.

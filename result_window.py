import tkinter as tk
from tkinter import ttk, messagebox
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load results
with open("encryption_results.json", "r") as f:
    results = json.load(f)

if not isinstance(results, list):
    messagebox.showerror("Error", "Invalid results format. Expected a list of runs.")
    exit()

# Root window
root = tk.Tk()
root.title("Encryption Results Viewer")
root.geometry("800x600")

# Selected run index
selected_run = tk.StringVar()
selected_run.set("Run #1")

# Frame for dropdown + table
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

# Dropdown menu
run_options = [f"Run #{i+1}" for i in range(len(results))]
dropdown = ttk.OptionMenu(frame_top, selected_run, run_options[0], *run_options)
dropdown.pack(side="left", padx=10)

# Table
tree = ttk.Treeview(root, columns=("metric", "value"), show="headings", height=8)
tree.heading("metric", text="Metric")
tree.heading("value", text="Value")
tree.pack(pady=20, fill="x")

# Chart frame
chart_frame = tk.Frame(root)
chart_frame.pack(fill="both", expand=True)

def display_run(index):
    """Update table and chart with selected run data"""
    for row in tree.get_children():
        tree.delete(row)

    run_data = results[index]

    # Fill table
    for key, value in run_data.items():
        if isinstance(value, (dict, list)):
            value = str(value)
        tree.insert("", "end", values=(key, value))

    # Clear chart frame
    for widget in chart_frame.winfo_children():
        widget.destroy()

    # Plot chart
    fig, ax = plt.subplots(figsize=(4, 3))
    metrics = ["encryption_time_ms", "decryption_time_ms"]
    values = [run_data.get(m, 0) for m in metrics]

    ax.bar(metrics, values, color=["blue", "green"])
    ax.set_ylabel("Time (ms)")
    ax.set_title("Encryption vs Decryption Time")

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# Dropdown callback
def on_run_change(*args):
    index = run_options.index(selected_run.get())
    display_run(index)

selected_run.trace("w", on_run_change)

# Initial display
display_run(0)

root.mainloop()

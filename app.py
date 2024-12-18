import tkinter as tk
from tkinter import filedialog, messagebox
from collections import Counter
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

# Compile the regex pattern outside of the loop for efficiency
ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

# Global variables to store the log counts
log_counts = Counter()  
ip_counts = Counter()

# Function to analyze logs efficiently
def analyze_logs(file_path, callback):
    global log_counts, ip_counts
    log_counts.clear()  # Clear previous counts
    ip_counts.clear()

    try:
        with open(file_path, "r") as file:
            # Read the file in batches for better performance
            lines = []
            for line in file:
                lines.append(line)
                if len(lines) >= 1000:  # Process in batches of 1000 lines
                    process_batch(lines, log_counts, ip_counts)
                    lines.clear()
            # Process remaining lines
            if lines:
                process_batch(lines, log_counts, ip_counts)

        # Call the callback function to update the GUI with results
        callback(log_counts, ip_counts)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to analyze logs: {e}")

# Function to process each batch of log lines
def process_batch(lines, log_counts, ip_counts):
    for line in lines:
        # Count log levels
        if "INFO" in line:
            log_counts["INFO"] += 1
        elif "ERROR" in line:
            log_counts["ERROR"] += 1
        elif "WARNING" in line:
            log_counts["WARNING"] += 1

        # Find IP addresses using the pre-compiled regex pattern
        ip_match = ip_pattern.findall(line)
        if ip_match:
            ip_counts.update(ip_match)

# Function to display graphs for log counts and IPs
def display_graphs(log_counts, ip_counts):
    # Create a new window for graphs
    graph_window = tk.Toplevel(root)
    graph_window.title("Log Analysis Graphs")
    graph_window.geometry("800x600")
    graph_window.configure(bg="#f0f8ff")

    # Create matplotlib figures
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Log Analysis Results")

    # Bar graph for log levels
    ax1.bar(log_counts.keys(), log_counts.values(), color=['#3498db', '#e74c3c', '#f39c12'])
    ax1.set_title("Log Levels")
    ax1.set_ylabel("Count")

    # Bar graph for top 10 IPs
    top_ips = ip_counts.most_common(10)
    ip_labels, ip_values = zip(*top_ips) if top_ips else ([], [])
    ax2.bar(ip_labels, ip_values, color='#2ecc71')
    ax2.set_title("Top 10 IP Addresses")
    ax2.set_ylabel("Occurrences")
    ax2.set_xticklabels(ip_labels, rotation=45, ha="right")

    # Embed the plot into the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)

# Function to save the result log to a file
def save_log():
    try:
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if save_path:
            with open(save_path, "w") as file:
                file.write("Log Level Counts:\n")
                for log_level, count in log_counts.items():
                    file.write(f"{log_level}: {count}\n")

                file.write("\nTop 10 IP Addresses:\n")
                top_ips = ip_counts.most_common(10)
                for ip, count in top_ips:
                    file.write(f"{ip}: {count}\n")

            messagebox.showinfo("Success", "Results saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save results: {e}")

# Function to select a log file
def select_log_file():
    file_path = filedialog.askopenfilename(title="Select Log File", filetypes=[("Log Files", "*.log"), ("All Files", "*.*")])
    if file_path:
        analyze_logs(file_path, display_graphs)

# Function to exit the application
def exit_app():
    root.quit()  # Stop the Tkinter main loop
    root.destroy()  # Destroy the root window and free up resources

# Main GUI setup
root = tk.Tk()
root.title("Cybersecurity Log Analyzer")
root.geometry("400x300")
root.configure(bg="#e6f2ff")

# Add the .ico file to the main window using iconphoto
try:
    icon_image = Image.open("IMG_20241027_230002.ico")  # Open the .ico file using PIL
    photo = ImageTk.PhotoImage(icon_image)  # Convert the image to a Tkinter-compatible format
    root.iconphoto(True, photo)  # Set the window icon using the image
except Exception as e:
    print(f"Icon not loaded for main window: {e}")

# Title Label
title_label = tk.Label(root, text="Cybersecurity Log Analyzer", font=("Helvetica", 16, "bold"), bg="#e6f2ff", fg="#2c3e50")
title_label.pack(pady=20)

# Select Log File Button
select_button = tk.Button(root, text="Select Log File", command=select_log_file, bg="#3498db", fg="white", font=("Helvetica", 12, "bold"), padx=10, pady=5)
select_button.pack(pady=10)

# Save Results Button
save_button = tk.Button(root, text="Save Results", command=save_log, bg="#2ecc71", fg="white", font=("Helvetica", 12, "bold"), padx=10, pady=5)
save_button.pack(pady=10)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=exit_app, bg="#e74c3c", fg="white", font=("Helvetica", 12, "bold"), padx=10, pady=5)
exit_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
